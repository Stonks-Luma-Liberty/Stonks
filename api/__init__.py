from lru import LRU

coingecko_coin_lookup_cache = LRU(5)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 "
                  "Safari/537.36 "
}
