import sqlite3
import xml.etree.ElementTree as ET

class XMLUtils:
    @staticmethod
    def export_to_xml(table_name, output_file):
        """Exports a table's data to an XML file."""
        conn = sqlite3.connect("database/autodatabase.db")
        cursor = conn.cursor()

        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]

            root = ET.Element(table_name)
            for row in rows:
                record = ET.SubElement(root, "record")
                for col_name, col_value in zip(column_names, row):
                    element = ET.SubElement(record, col_name)
                    element.text = str(col_value) if col_value is not None else ""

            tree = ET.ElementTree(root)
            tree.write(output_file)
            print(f"Exported {table_name} to {output_file}")
        except sqlite3.Error as e:
            print(f"Error exporting to XML: {e}")
        finally:
            conn.close()

    @staticmethod
    def import_from_xml(input_file):
        """Imports data from an XML file into the database."""
        tree = ET.parse(input_file)
        root = tree.getroot()
        table_name = root.tag

        conn = sqlite3.connect("database/autodatabase.db")
        cursor = conn.cursor()

        try:
            for record in root:
                columns = [child.tag for child in record]
                values = [child.text for child in record]
                placeholders = ", ".join(["?" for _ in columns])
                cursor.execute(
                    f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
                    values,
                )
            conn.commit()
            print(f"Imported data from {input_file} into {table_name}")
        except sqlite3.Error as e:
            print(f"Error importing from XML: {e}")
        finally:
            conn.close()

    @staticmethod
    def retrieve_data_from_xml(input_file, field_name):
        """Retrieve specific data from a given XML field."""
        tree = ET.parse(input_file)
        root = tree.getroot()

        results = []
        try:
            for record in root.findall("record"):
                field = record.find(field_name)
                if field is not None:
                    results.append(field.text)
        except Exception as e:
            print(f"Error retrieving data from XML: {e}")
        print(f"Retrieved data for field '{field_name}': {results}")
        return results

    @staticmethod
    def modify_xml_field(input_file, output_file, field_name, old_value, new_value):
        """Modify specific fields in an XML file."""
        tree = ET.parse(input_file)
        root = tree.getroot()

        try:
            for record in root.findall("record"):
                field = record.find(field_name)
                if field is not None and field.text == old_value:
                    field.text = new_value
        except Exception as e:
            print(f"Error modifying XML field: {e}")

        tree.write(output_file)
        print(f"Modified XML file saved to {output_file}")
