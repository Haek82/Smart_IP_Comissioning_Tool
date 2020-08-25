from openpyxl import load_workbook
import json

class Xlsx:
    #This is the excel import / export class

    def __init__(self, filename):

        self.workbook = load_workbook(filename=filename)
        self.sheet = self.workbook.active
        self.speakers = []
        self.importFromExcel()
        self.filename = filename

    def importFromExcel(self):
        for row in self.sheet.iter_rows(min_row=2, min_col=1, max_col=5, values_only=True):
            speaker = {
                "barcode" : row[0],
                "ip": row[1],
                "mask": row[2],
                "gw": row[3]
                }

            self.speakers.append(speaker)

    def setDanteNameAndMac(self, row, name, mac):
        macCell = "E" + str(row)
        danteCell = "F" + str(row)
        self.sheet[macCell] = mac
        self.sheet[danteCell] = name
        self.workbook.save(filename=self.filename)

    def printAllSpeakersInExcel(self):
        print("Speaker infomation in excel: ")
        for speaker in self.speakers:
            print(speaker)

    def getList(self):
        return self.speakers
