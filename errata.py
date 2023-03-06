import datetime
import logging
import xml.etree.ElementTree as ET


class ErrataReferenceXMLView:
    def __init__(self, root: ET.Element):
        if 'href' in root.attrib:
            self.href = root.attrib['href']
        if 'id' in root.attrib:
            self.id = root.attrib['id']
        if 'title' in root.attrib:
            self.title = root.attrib['title']
        if 'type' in root.attrib:
            self.type = root.attrib['type']


class ErrataCollectionXMLView:
    def __init__(self, root: ET.Element):
        self.packages = []
        self.name = root.find('name').text
        for package in root.findall('package'):
            self.packages.append(ErrataPackageXMLView(package))


class ErrataPackageXMLView:
    def __init__(self, root: ET.Element):
        self.arch = root.attrib['arch']
        self.epoch = root.attrib['epoch']
        self.name = root.attrib['name']
        self.release = root.attrib['release']
        self.src = root.attrib['src']
        self.version = root.attrib['version']
        self.filename = root.find('filename').text
        self.sum = ErrataSumXMLView(root.find('sum'))


class ErrataSumXMLView:
    def __init__(self, root: ET.Element):
        self.type = root.attrib['type']
        self.value = root.text


class ErrataUpdateXMLView:
    def __init__(self, root: ET.Element):
        self.from_ = root.attrib['from']
        self.status = root.attrib['status']
        self.type = root.attrib['type']
        self.version = root.attrib['version']
        self.id = root.find('id').text
        self.title = root.find('title').text
        self.rights = root.find('rights').text
        self.release = root.find('release').text
        self.description = root.find('description').text
        self.severity = root.find('severity').text
        self.solution = root.find('solution').text
        self.summary = root.find('summary').text
        self.pushcount = root.find('pushcount').text
        self.issued = self._format_date(root.find('issued').attrib['date'])
        self.updated = self._format_date(root.find('updated').attrib['date'])
        self.references = []
        if (len(root.find('references').findall('reference')) == 0 and
                len(root.find('references').attrib) == 0):
            logging.warning(f'errata update {self.id} references is empty')

        if len(root.find('references').attrib) > 0:
            logging.warning(f'errata update {self.id} has references with attributes.'
                            f'Probably errata format is corrupted. Creating an entry'
                            f' from these attributes.')
            self.references.append(ErrataReferenceXMLView(root.find('references')))

        for ref in root.find('references').findall('reference'):
            self.references.append(ErrataReferenceXMLView(ref))

        self.pkglist = []
        for collection in root.find('pkglist').findall('collection'):
            self.pkglist.append(ErrataCollectionXMLView(collection))

    def _format_date(self, date_str: str) -> datetime.datetime:
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %Z')
        except ValueError:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


class ErrataXMLView:
    """
    Representation of Errata based on updateinfo.xml fields
    """

    def __init__(self, root: ET.Element):
        self.updates = []
        for update in root.findall('update'):
            self.updates.append(ErrataUpdateXMLView(update))
