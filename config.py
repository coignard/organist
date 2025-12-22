ORGANTEQ_URL = "http://localhost:8081/jsonrpc"

KEYBOARD_NAMES = {
    1: "Pedal",
    2: "Rückpositiv",
    3: "Hauptwerk",
    4: "Schwellwerk",
}

CC_TO_STOP_NAME = {
    1: "Prinzipal 32'",
    2: "Gross Untersatz 32'",
    3: "Prinzipal 16'",
    4: "Kontra Bass 16'",
    5: "Gross Untersatz 16'",
    6: "Gross Quintaden 16'",
    7: "Prinzipal 8'",
    8: "Octav 8'",
    9: "Viol Gamba 8'",
    10: "Unda Maris 8'",
    11: "Flöte 8'",
    12: "Doppel Flute 8'",
    13: "Gedact 8'",
    14: "Nachthorn 8'",
    15: "Celinder Quinta 5'1/3",
    16: "Prinzipal 4'",
    17: "Flöte 4'",
    18: "Celinder Quinta 2'2/3",
    19: "Nassad Quinta 2'2/3",
    20: "Super Octav 2'",
    21: "Waldflöte 2'",
    22: "Tertia 1'3/5",
    23: "Sifflöte 1'1/3",
    24: "Sesquialtera 2f.",
    25: "Zimbel 3 f.",
    26: "Mixtura 4f.",
    27: "Mixtura 8f.",
    28: "Posaunen Bass 32'",
    29: "Posaunen Bass 16'",
    30: "Fagott 16'",
    31: "Trommet 8'",
    32: "Krumhorn 8'",
    33: "Barpfeife 8'",
    34: "Vox Humana 8'",
    35: "Schalmei 4'",
    36: "Zinke 2'",
    37: "Principal 32'",
    38: "Bourdon 32'",
    39: "Montre 16'",
    40: "Principal 16'",
    41: "Bourdon 16'",
    42: "Quintaton 16'",
    43: "Montre 8'",
    44: "Principal 8'",
    45: "Gambe 8'",
    46: "Voix Celeste 8'",
    47: "Salicional 8'",
    48: "Flute 8'",
    49: "Flute Traversiere 8'",
    50: "Flute Harmonique 8'",
    51: "Bourdon 8'",
    52: "Prestant 4'",
    53: "Principal 4'",
    54: "Flute 4'",
    55: "Grande Tierce 3'1/5",
    56: "Quinte 2'2/3",
    57: "Nasard 2'2/3",
    58: "Doublette 2'",
    59: "Tierce 1'3/5",
    60: "Larigot 1'1/3",
    61: "Septieme 1'1/7",
    62: "Piccolo 1'",
    63: "Cornet V",
    64: "Plein Jeu III",
    65: "Plein Jeu V",
    66: "Contre Bombarde 32'",
    67: "Bombarde 16'",
    68: "Basson 16'",
    69: "Trompette 8'",
    70: "Clarinette 8'",
    71: "Hautbois 8'",
    72: "Musette 8'",
    73: "Regale 8'",
    74: "Voix Humeine 8'",
    75: "Clairon 4'",
}

CC_TO_COUPLER = {
    76: ("Coupler Switch[1]", "Coupler 1"),
    77: ("Coupler Switch[2]", "Coupler 2"),
    78: ("Coupler Switch[3]", "Coupler 3"),
    79: ("Coupler Switch[4]", "Coupler 4"),
    80: ("Coupler Switch[5]", "Coupler 5"),
    81: ("Coupler Switch[6]", "Coupler 6"),
}

CC_TO_MONO_COUPLER = {
    82: ("Mono Coupler Switch[1]", "Mono Coupler 1"),
    83: ("Mono Coupler Switch[2]", "Mono Coupler 2"),
    84: ("Mono Coupler Switch[3]", "Mono Coupler 3"),
    85: ("Mono Coupler Switch[4]", "Mono Coupler 4"),
}

CC_TO_TREMULANT = {
    86: ("Tremulant Switch[1]", "Tremulant 1"),
    87: ("Tremulant Switch[2]", "Tremulant 2"),
    88: ("Tremulant Switch[3]", "Tremulant 3"),
    89: ("Tremulant Switch[4]", "Tremulant 4"),
}

CC_TO_TUTTI = {
    90: ("Tutti", "Tutti"),
}

PC_TO_COMBINATION = {
    10: "Combination 1",
    11: "Combination 2",
    12: "Combination 3",
    13: "Combination 4",
    14: "Combination 5",
    15: "Combination 6",
    16: "Combination 7",
    17: "Combination 8",
    18: "Combination 9",
    19: "Combination 10",
}

LOG_LEVEL_COLORS = {
    "INFO": "#888",
    "WARNING": "#FFA100",
    "ERROR": "#ff5555",
}

MAX_CONSOLE_LINES = 100
FLASH_DURATION_SECONDS = 0.05
REQUEST_TIMEOUT_SECONDS = 2
