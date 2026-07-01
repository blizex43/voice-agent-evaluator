# Bug Report

## Summary

Test calls were made against the Pretty Good AI assessment line using the scenarios in this repository. This report documents quality issues found in the AI agent's responses, with references to transcripts and recordings where available.

## Bug 1: Agent 
LLM: llama-3.1-8b-instant
Voice: English-Unknown
Severity: Medium  
Call: `output/transcripts/CAd6566bf848f36089fc2015dcfbd4fd17.md`  
Recording: `C:\Users\Jonathan\Downloads\Python Private\voice-agent-evaluator\output\recordings\RE505f5e950510bb4f818bcf9fa3154965.mp3`  
Timestamp: `1:07`

Details:
Even when given incomplete details from the patient, the LLM does good in clarifying their right which is good. But then, when the patient is busy trying to think about their question which might give them time to answer, the auto-listener thinks they are done talking, then signals the completed flag. There should be some time until the agent finally wants to end the full call without any voice input from the recieving end. At least a static number like **10 seconds**.

## Bug 2: Agent 

LLM: llama-3.1-8b-instant
Voice: English-Danielle-Generative
Severity: Low  
Call: `output/transcripts/CA0239badedb73dc0ea024e02a9b0c4495.md`  
Recording: `C:\Users\Jonathan\Downloads\Python Private\voice-agent-evaluator\output\recordings\REd010722557c71f2c23e2888dba5f1ced.mp3`  
Timestamp: `0:24, 0:40, 1:05`

Details:
There was a constant timeout of 10 seconds every time I relay back to the agent. I couldn't talk for more than 10 seconds before getting cut out.

...