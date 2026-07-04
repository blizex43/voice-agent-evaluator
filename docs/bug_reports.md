# Bug Report

## Summary

Test calls were made against the Pretty Good AI assessment line using the scenarios in this repository. This report documents quality issues found in the AI agent's responses, with references to transcripts and recordings where available.

## Bug 1: Assistant Agent

LLM: llama-3.1-8b-instant
Voice: English-Unknown
Severity: Low-Medium  
Call: `C:\Users\Jonathan\Downloads\Python Private\voice-agent-evaluator\output\transcripts\transcript_01.md`  
Recording: `C:\Users\Jonathan\Downloads\Python Private\voice-agent-evaluator\output\recordings\recording_01.mp3`  
Timestamp: `0:05-2:03`

Details:
Throughout the call, I could tell that when the other end was about to respond, the assistant would typewrite then respond which makes it sound more real. The problem is that when my agent is speaking while pausing, the agent will start to typewrite even after commas and short pauses. The agent needs to wait slightly longer, maybe at least 0.3 seconds longer before playing the typewriter, unless that's meant to be there.

## Bug 2: Assistant Agent

LLM: llama-3.1-8b-instant
Voice: English-Unknown
Severity: Medium  
Call: `C:\Users\Jonathan\Downloads\Python Private\voice-agent-evaluator\output\transcripts\transcript_01.md`  
Recording: `C:\Users\Jonathan\Downloads\Python Private\voice-agent-evaluator\output\recordings\recording_01.mp3`  
Timestamp: `1:51`

Details:
While the patient was explaining why they were confused and clarify that they need to speak with their doctor, the assistant abruptly cut them off after the slight pause. Reffering to Bug 1, the assistant needs to be able to wait a little, typewrite some more (for more time for my patient to possibly say another line), then the assistant can respond. Along with this, the assistant ignored the patients requests and still sent them to the unrelated "patient support team" instead of their doctor.

## Bug 3: Patient Agent

LLM: llama-3.1-8b-instant
Voice: English-Unknown
Severity: Medium  
Call: `C:\Users\Jonathan\Downloads\Python Private\voice-agent-evaluator\output\transcripts\transcript_01.md`  
Recording: `C:\Users\Jonathan\Downloads\Python Private\voice-agent-evaluator\output\recordings\recording_01.mp3`  
Timestamp: `0:05`

Details:
The automated message at the start was responded to by the patient. The patient should ignore it and only respond when the assistant talks.

Solution:
Added blacklisted phrases so the agent can return an empty response to ignore and listen to the next message.

## Bug 4: Patient Agent

LLM: llama-3.1-8b-instant
Voice: English-Unknown
Severity: High  
Call: `C:\Users\Jonathan\Downloads\Python Private\voice-agent-evaluator\output\transcripts\transcript_01.md`  
Recording: `C:\Users\Jonathan\Downloads\Python Private\voice-agent-evaluator\output\recordings\recording_01.mp3`  
Timestamp: `0:05`

Details:
When the assistant told the patient to wait a moment, the patient responded with a complete full-fledged response, then the assistant talked as soon as the patient spoke so they started both talking over eachother

Solution:
Adjusted the voice timeout by +66%
Added keywords that will also wait for the assistant to finish: [1 moment while, one moment while]

## Bug 5: Assistant Agent

LLM: llama-3.1-8b-instant
Voice: English-Unknown
Severity: High  
Call: `C:\Users\Jonathan\Downloads\Python Private\voice-agent-evaluator\output\transcripts\transcript_02.md`  
Recording: `None`  
Timestamp: `Unavailable`

Details:
Mid conversation, the assistant agent failed to respond and left my patient hanging without ending the call. The patient was not able to fetch the recording.

Patient Solution: Lower the timeout to 30 seconds.

...
