from enum import Enum, unique


@unique
class Network(str, Enum):
    APTOS = "aptos"
    ARBITRUM_ONE = "arbitrum-one"
    AVAX_C = "avax-c"
    BASE = "base"
    BSC = "bsc"
    CELO = "celo"
    CORE = "core"
    ETHEREUM = "ethereum"
    FANTOM = "fantom"
    LINEA = "linea"
    OPBNB = "opbnb"
    OP_MAINNET = "op-mainnet"
    POLYGON = "polygon"
    POLYGON_ZKEVM = "polygon-zkevm"
    SCROLL = "scroll"
    SOLANA = "solana"
    STARKNET = "starknet"
    ZKSYNC_ERA = "zksync-era"
    ZORA = "zora"
