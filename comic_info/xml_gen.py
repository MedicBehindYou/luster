from lxml import etree

class ComicInfo:
    def __init__(self):
        self.root = etree.Element("ComicInfo")

    def set_element(self, name, value):
        element = etree.SubElement(self.root, name)
        element.text = str(value)

    def set_attribute(self, element, name, value):
        element.set(name, str(value))

    def save(self, filename):
        etree.ElementTree(self.root).write(filename, pretty_print=True, encoding="utf-8", xml_declaration=True)

    def validate(self, schema_file):
        schema = etree.XMLSchema(file=schema_file)
        parser = etree.XMLParser(schema=schema)
        try:
            etree.fromstring(etree.tostring(self.root), parser)
            return True
        except etree.XMLSyntaxError as e:
            print("Validation Error:", e)
            return False

if __name__ == "__main__":
    comic = ComicInfo()
    comic.set_element("Title", "Comic Title")
    comic.set_element("Series", "Comic Series")
    comic.set_element("Number", "1")
    comic.set_element("PageCount", 20)
    comic.add_page_info(image=1, page_type="FrontCover")
    comic.add_page_info(image=2, page_type="Story")
    comic.save("example_comicinfo.xml")

    if comic.validate("comicinfo.xsd"):
        print("Validation successful")
    else:
        print("Validation failed")
