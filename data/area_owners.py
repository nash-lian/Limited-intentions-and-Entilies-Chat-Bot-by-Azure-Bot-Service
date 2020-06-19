# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import pandas as pd

class AreaOwners(object):

    area_owners = []
    org_areas = []
    areas = []

    @staticmethod
    def initialize():

        if len(AreaOwners.area_owners) == 0:
            AreaOwners.area_owners = pd.read_csv('./data/AIAreaOwners.csv', index_col='Area')
            
            AreaOwners.org_areas = AreaOwners.area_owners.index            
            AreaOwners.area_owners.index = [x.capitalize() for x in AreaOwners.area_owners.index]
            AreaOwners.areas = AreaOwners.area_owners.index

    @staticmethod
    def OwnerInfo(area):

        if len(AreaOwners.area_owners) == 0:
            AreaOwners.initialize()
        
        area = area.capitalize()
        info_row = []

        if area in AreaOwners.areas:
            info_row = AreaOwners.area_owners.loc[area, :]
        else:
            return f'The team for {area} is not found'

        ret = ''
        if isinstance(info_row['PM'], str):
            ret += 'The PM contact: ' + info_row['PM'].strip()
            if isinstance(info_row['PM Email'], str):
                ret += ' at ' + info_row['PM Email'].replace(';','').strip()

        if isinstance(info_row['Dev'], str):
            if len(ret) > 0:
                ret += ", and t"
            else:
                ret += 'T'
            ret += 'he dev contact: ' + info_row['Dev'].strip()
            if isinstance(info_row['Dev Email'], str):
                ret += ' at ' + info_row['Dev Email'].replace(';','').strip()

        return ret