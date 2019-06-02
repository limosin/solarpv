from pvlib.pvsystem import retrieve_sam

def get_panel_list():
    panel_list = list([])
    avlb_mods = ['SandiaMod', 'CECMod']
    for mods in avlb_mods:
        panel_list = panel_list+retrieve_sam(mods).columns.values.tolist()
    return panel_list

def get_inv_list():
    inv_list = list([])
    avlb_invs = ['CECInverter', 'SandiaInverter', 'ADRInverter']
    for invs in avlb_invs:
        inv_list = inv_list+retrieve_sam(invs).columns.values.tolist()
    return inv_list

if __name__ == '__main__':
    panel_list = get_panel_list()
    print(len(panel_list))
    # print(panel_list[0:10])
    inv_list = get_inv_list()
    print(len(inv_list))