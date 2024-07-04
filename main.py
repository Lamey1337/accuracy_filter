from osu_scores import OsuScores
from struct import pack

def getULEBString(string):
    uleb = pack('b', 0x0b)
    val = len(string)
    # pack length of string
    while val != 0:
        # get low order 7 bits and shift
        byte = (val & 0x7F)
        val >>= 7
        # more values to come: set high order bit
        if val != 0:
            byte |= 0x80

        uleb += pack('B', byte)

    str_format = str(len(string)) + 's'

    uleb += pack(str_format, bytes(str(string), "utf-8"))

    return uleb

def writeCollectionDB(version, collections):
    out = open('./collection.db', 'wb')
    out.write(pack('I', version))
    out.write(pack('I', len(collections)))

    for collection in collections:

        cname, hashes = collection[0], collection[1]
        out.write(getULEBString(cname))
        out.write(pack('I', len(hashes)))
        for md5 in hashes:
            out.write(getULEBString(md5))

    out.close()

osu_scores_path = "./scores.db"

mania_99 = []
mania_05 = []
mania_08 = []
mania_100 = []
osuScores = OsuScores.from_file(osu_scores_path)

for beatmap in osuScores.beatmaps:
    acc_list = []
    for score in beatmap.scores:

        if score.gameplay_mode == 3:
            all_300 = score.num_300 + score.num_gekis
            all_200 = score.num_katus
            all_100 = score.num_100
            all_50  = score.num_50
            all_notes = sum([all_300, all_200, all_100, all_50, score.num_miss])
            accuracy = (300 * all_300 + 200 * all_200 + 100 * all_100 + 50 * all_50) / (300 * all_notes) 
            accuracy *= 100
            acc_list.append({"hash": score.beatmap_md5_hash.value, "acc": accuracy})
    
    acc_list.sort(key=lambda x: x["acc"])
    if acc_list:
        item = acc_list.pop()

        if item["acc"] < 100:
            mania_100.append(item["hash"])
        if item["acc"] < 99.8:
            mania_08.append(item["hash"])
        if item["acc"] < 99.5:
            mania_05.append(item["hash"])
        if item["acc"] < 99:
            mania_99.append(item["hash"])

version = 20191031
c1 = [
    "99% mania",
    mania_99
]
c2 = [
    "99.5% mania",
    mania_05
]
c3 =  [
    "99.8% mania",
    mania_08
]
c4 = [
    "100% mania",
    mania_100
]

collections = [c1, c2, c3, c4]

writeCollectionDB(version, collections)