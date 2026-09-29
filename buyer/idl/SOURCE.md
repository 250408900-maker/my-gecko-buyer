# Where this IDL comes from

`let_me_buy.idl.json` is the published Anchor IDL of the `let_me_buy` program
(`BUYuxRfhCMWavaUWxhGtPP3ksKEDZxCD5gzknk3JfAya`, the same address on devnet and mainnet),
vendored unchanged from Gecko's repository (`capabilities/let_me_buy.idl.json` in
`surfcall`), which is the copy the hosted MCP reads. The program is Let Me Buy's
(letmebuy.app). `buyer/letmebuy.py` encodes and decodes from it, and the encoder is a
small subset of Gecko's `gecko/instruction_build.py`.
