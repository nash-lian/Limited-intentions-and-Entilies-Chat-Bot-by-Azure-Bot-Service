# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
from data import AreaOwners

class AreaDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(AreaDialog, self).__init__(dialog_id or AreaDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.area_step,
                    self.final_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    async def area_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If an area has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        area_details = step_context.options

        if area_details.area is None:
            message_text = f"Which AI area you want to know?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(area_details)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Complete the interaction and end the dialog.
        :param step_context:
        :return DialogTurnResult:
        """
        if step_context.result:
            area_details = step_context.options

            return await step_context.end_dialog(area_details)
        return await step_context.end_dialog()
