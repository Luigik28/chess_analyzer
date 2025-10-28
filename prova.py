from stockfish import Stockfish

sf = Stockfish(path="stockfish/stockfish.exe")
print(sf.get_stockfish_major_version())