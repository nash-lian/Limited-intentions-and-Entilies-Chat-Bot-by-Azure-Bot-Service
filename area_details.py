# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class AreaDetails:
    def __init__(
        self,
        area: str = None,
            unsupported_area=None,
    ):
        if unsupported_area is None:
            unsupported_area = []
        self.area = area
        self.unsupported_area = unsupported_area
