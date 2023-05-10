almalinux9_ecosystem = 'AlmaLinux:9'
almalinux8_ecosystem = 'AlmaLinux:8'

"""
mapping of collection name to ecosystem name
collection name is regex of all possible names of the collection
"""
collection_name_to_ecosystem = {
    # AlmaLinux 9 collection names
    r'almalinux-9.*': almalinux9_ecosystem,
    # AlmaLinux 8 collection names
    r'almalinux-8.*': almalinux8_ecosystem,
}
