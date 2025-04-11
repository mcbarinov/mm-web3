from __future__ import annotations

from enum import Enum, unique


@unique
class NetworkType(str, Enum):
    EVM = "evm"
    SOLANA = "solana"
    APTOS = "aptos"
    STARKNET = "starknet"

    def lowercase_address(self) -> bool:
        match self:
            case NetworkType.EVM:
                return True
            case NetworkType.SOLANA:
                return False
            case NetworkType.APTOS:
                return True
            case NetworkType.STARKNET:
                return True
        raise ValueError("no network found")


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

    @property
    def network_type(self) -> NetworkType:
        if self in self.evm_networks():
            return NetworkType.EVM
        if self in self.solana_networks():
            return NetworkType.SOLANA
        if self in self.aptos_networks():
            return NetworkType.APTOS
        if self in self.starknet_networks():
            return NetworkType.STARKNET
        raise ValueError("no network found")

    @classmethod
    def evm_networks(cls) -> list[Network]:
        return [
            Network.ARBITRUM_ONE,
            Network.AVAX_C,
            Network.BASE,
            Network.BSC,
            Network.CELO,
            Network.CORE,
            Network.ETHEREUM,
            Network.FANTOM,
            Network.LINEA,
            Network.OPBNB,
            Network.OP_MAINNET,
            Network.POLYGON,
            Network.POLYGON_ZKEVM,
            Network.SCROLL,
            Network.ZKSYNC_ERA,
            Network.ZORA,
        ]

    @classmethod
    def solana_networks(cls) -> list[Network]:
        return [Network.SOLANA]

    @classmethod
    def aptos_networks(cls) -> list[Network]:
        return [Network.APTOS]

    @classmethod
    def starknet_networks(cls) -> list[Network]:
        return [Network.STARKNET]
