# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, TurnContext
from botbuilder.schema import InputHints, SuggestedActions, CardAction, ActionTypes

from area_details import AreaDetails
from area_recognizer import AreaRecognizer
from helpers.luis_helper import LuisHelper, Intent
from .area_dialog import AreaDialog
from data import AreaOwners

class MainDialog(ComponentDialog):
    def __init__(
        self, luis_recognizer: AreaRecognizer, area_dialog: AreaDialog
    ):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self._firstRun = True
        self._luis_recognizer = luis_recognizer
        self._area_dialog_id = area_dialog.id

        self.add_dialog(ChoicePrompt("cardPrompt"))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(area_dialog)
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.intro_step, self.act_step, self.final_step]
            )
        )

        self.initial_dialog_id = "WFDialog"

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
            )

            return await step_context.next(None)

        if self._firstRun:
            self._firstRun = False
            card_options = [Choice(synonyms=[area], value=area) for area in AreaOwners.org_areas]
            return await step_context.prompt(
                        "cardPrompt",
                        PromptOptions(
                            prompt=MessageFactory.text(
                                "Please select the AI area. We will find their contact for you."
                            ),
                            choices=card_options
                        ),
                    )

        message_text = (
            str(step_context.options)
            if step_context.options
            else "Please tell me the AI area. We will find their contact for you."
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def act_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            # LUIS is not configured, we just run the AreaDialog path with an empty AreaDetails Instance.
            return await step_context.begin_dialog(
                self._area_dialog_id, AreaDetails()
            )

        # Call LUIS and gather any potential area details. (Note the TurnContext has the response to the prompt.)
        intent, luis_result = await LuisHelper.execute_luis_query(
            self._luis_recognizer, step_context.context
        )

        if intent == Intent.QUERY_OWNER.value and luis_result:
            # Show a warning for Origin and Destination if we can't resolve them.
            await MainDialog._show_warning_for_unsupported_areas(
                step_context.context, luis_result
            )

            # Run the BookingDialog giving it whatever details we have from the LUIS call.
            return await step_context.begin_dialog(self._area_dialog_id, luis_result)

        if intent == Intent.AREA_LIST.value:
            self._firstRun = True

        else:
            didnt_understand_text = (
                "Sorry, I didn't get that. Please try asking in a different way"
            )
            didnt_understand_message = MessageFactory.text(
                didnt_understand_text, didnt_understand_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(didnt_understand_message)

        return await step_context.next(None)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # If the child dialog ("AreaDialog") was cancelled or the user failed to confirm,
        # the Result here will be null.
        if step_context.result is not None:
            result = step_context.result

            if result.area is not None:
                msg_txt = AreaOwners.OwnerInfo(result.area)
                message = MessageFactory.text(msg_txt, msg_txt, InputHints.ignoring_input)
                await step_context.context.send_activity(message)

        prompt_message = "Please tell me the AI area. We will find their contacts for you."
        return await step_context.replace_dialog(self.id, prompt_message)

    @staticmethod
    async def _show_warning_for_unsupported_areas(
        context: TurnContext, luis_result: AreaDetails
    ) -> None:
        if luis_result.unsupported_area:
            message_text = (
                f"Sorry but the following AI area are not supported:"
                f" {', '.join(luis_result.unsupported_area)}"
            )
            message = MessageFactory.text(
                message_text, message_text, InputHints.ignoring_input
            )
            await context.send_activity(message)
