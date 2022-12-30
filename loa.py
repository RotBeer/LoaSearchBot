import sqlite3
import requests
import os
import json

class Loa_search():
    def __init__(self):
        self.base_url = 'https://developer-lostark.game.onstove.com'
        self.auth = f"bearer {os.environ['lost_ark_api']}"        
        self.save_auctions_options()
        self.init_db()

    def create(self, data: dict):
        con = sqlite3.connect('test.db')
        cur = con.cursor()
        cols = ['User_id', 'ItemGradeQuality', 'CategoryCode', 'ItemGrade']
        vals = [data[col] for col in cols]
        query = cur.execute(f"INSERT INTO AuctionItems ({', '.join(cols)}) VALUES (?, ?, ?, ?)", tuple(vals))
        lastrowid = query.lastrowid
        cols = ['AuctionItemsId', 'FirstOption', 'SecondOption', 'MinValue']
        options = [(lastrowid, op['FirstOption'], op['SecondOption'], op.get('MinValue', 0)) for op in data.get('EtcOptions')]
        cur.executemany(f"INSERT INTO EtcOptions ({', '.join(cols)}) VALUES (?, ?, ?, ?)", options)
        con.commit()
        con.close()
        return True

    def read(self, user_id) -> list:
        res = []
        con = sqlite3.connect('test.db')
        cur = con.cursor()
        rows = cur.execute(f"SELECT * FROM AuctionItems WHERE User_id = '{user_id}'")
        for row in rows.fetchall():
            ops = cur.execute(f"SELECT * FROM EtcOptions WHERE AuctionItemsId = '{row[0]}'")
            temp = {'Id': row[0], 'User_id': row[1], 'ItemGradeQuality': row[2], 'CategoryCode': row[3], 'ItemGrade': row[4], 'EtcOptions': []}
            temp['EtcOptions'] = [{'FirstOption': op[2], 'SecondOption': op[3]} for op in ops.fetchall()]
            res.append(temp)
        con.close()
        return res

    def update(self):
        pass

    def delete(self, Id):
        con = sqlite3.connect('test.db')
        cur = con.cursor()
        cur.execute('PRAGMA foreign_keys = ON')
        cur.execute(f"DELETE FROM Auctionitems WHERE Id = '{Id}'")
        con.commit()
        con.close()

    def search(self) -> list:
        res = []
        con = sqlite3.connect('test.db')
        cur = con.cursor()
        rows = cur.execute('SELECT * FROM AuctionItems')
        for row in rows.fetchall():
            ops = cur.execute(f"SELECT * FROM EtcOptions WHERE AuctionItemsId = '{row[0]}'")
            data = {'ItemGradeQuality': row[2], 'CategoryCode': row[3], 'ItemGrade': row[4], 'EtcOptions': []}
            data['EtcOptions'] = [{'FirstOption': op[2], 'SecondOption': op[3]} for op in ops.fetchall()]
            response = requests.post(self.base_url+'/auctions/items', headers={'authorization': self.auth}, json=data)
            body = response.json()
            if body.get('TotalCount') > 0:
                for item in body['Items'][:3]:
                    temp = {'User_id': row[1], 'Name': item['Name'], 'Grade': item['Grade'], 'GradeQuality': item['GradeQuality'], 'StartPrice': item['AuctionInfo']['StartPrice'], 'BuyPrice': item['AuctionInfo']['BuyPrice'], 'Options': []}
                    temp['Options'] = [{'Type': op['Type'], 'OptionName': op['OptionName'], 'Value': op['Value']} for op in item['Options']]
                    res.append(temp)
        return res

    def save_auctions_options(self):
        #for develop
        file_path = './autions_options.json'
        # if not os.path.exists(file_path):
        if True:
            response = requests.get(self.base_url+'/auctions/options', headers={'authorization': self.auth})
            with open(file_path, 'w', encoding='UTF-8') as file:
                json.dump(response.json(), file, indent=4, ensure_ascii=False)

        with open(file_path, encoding='UTF-8') as file:
            self.action_options = json.load(file)
    
    def init_db(self):
        con = sqlite3.connect('test.db')
        cur = con.cursor()
        # cur.execute('DROP TABLE IF EXISTS AuctionItems')
        # cur.execute('DROP TABLE IF EXISTS EtcOptions')
        cur.execute('''CREATE TABLE IF NOT EXISTS AuctionItems(
                        Id INTEGER PRIMARY KEY,
                        User_id varchar,
                        ItemGradeQuality INTEGER,
                        CategoryCode INTEGER,
                        ItemGrade varchar,
                        Created TIMESTAMP DEFAULT (DATETIME('now', 'localtime'))
                        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS EtcOptions(
                        Id INTEGER PRIMARY KEY,
                        AuctionItemsId INTEGER,
                        FirstOption INTEGER,
                        SecondOption INTEGER,
                        MinValue INTEGER,
                        FOREIGN KEY(AuctionItemsId) REFERENCES AuctionItems(Id) ON DELETE CASCADE
                        )''')
        con.commit()
        con.close()

if __name__ == "__main__":
    loa = Loa_search()

    data = {'User_id': 'lee', 'ItemGradeQuality': 70, 'CategoryCode': 200010, 'ItemGrade': '고대',
        'EtcOptions': [{'FirstOption': 2, 'SecondOption': 18}, {'FirstOption': 2, 'SecondOption': 16}, {'FirstOption': 3, 'SecondOption': 118}]}
    res = loa.create(data)
    data = {'User_id': 'kim', 'ItemGradeQuality': 50, 'CategoryCode': 200010, 'ItemGrade': '고대',
        'EtcOptions': [{'FirstOption': 3, 'SecondOption': 118}, {'FirstOption': 2, 'SecondOption': 18}]}
    res = loa.create(data)

    print(loa.read('lee'))
    loa.delete(2)

    for i in loa.search():
        print(i)
        print()