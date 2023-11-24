# Whisper Benchmark
## Requirements
- Common benchmark 
- it seems that usefultransformers implementation does not implement word timestamps for whisper, making it probably hard to compare with the whisper-streaming implementation
- Whisper streaming uses timestamps for locality algorithm and to identify reoccuring words

## What to measure?
- Latency : in order to tell, whether this application is usable in a customer-facing application
- WER : same as above

## Idea Proposal
- Whisper-Streaming on Pi5 with faster-whisper backend and tiny-model
- Whisper-Edge integrated in Whisper-Streaming
- usefule-transformers without Whisper-Streaming Wrapper
