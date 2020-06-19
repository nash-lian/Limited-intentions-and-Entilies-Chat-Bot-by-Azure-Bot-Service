# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from area_details import AreaDetails


class Intent(Enum):
    QUERY_OWNER = "QueryOwner"
    CANCEL = "Cancel"
    AREA_LIST = "AIAreaList"
    NONE_INTENT = "None"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )

            if intent == Intent.QUERY_OWNER.value:
                result = AreaDetails()

                # We need to get the result from the LUIS JSON which at every level returns an array.
                area_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Area", []
                )
                if len(area_entities) > 0:
                    if recognizer_result.entities.get("Area", [{"$instance": {}}])[0][0]:
                        result.area = recognizer_result.entities.get("Area", [{"$instance": {}}])[0][0]
                    else:
                        result.unsupported_areae.append(
                            area_entities[0]["text"]
                        )

        except Exception as exception:
            print('LUIS exception:', exception)

        return intent, result
