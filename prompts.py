"""
LLM prompts for different aspects of chord refinement.
"""

# Bass reliability assessment prompt
BASS_RELIABILITY_PROMPT = """
As a music scholar specializing in bass analysis and chord theory, your task is to evaluate whether the chord recognition results from the bass stem are reliable enough to be used for correcting the chord recognition results from the original full mix.

I will provide:
1. Detected key information and its confidence level
2. Chord recognition results from the original full mix
3. Bass note recognition results from the bass stem only (include bass note information only, without chord quality)

Chord format: Each line includes the start time, end time, and chord label (e.g., "C:maj", "G:min/5")
Bass note recognition format: Each line includes the start time, end time, and bass note (e.g., "C", "G", "E")

DETECTED KEY INFORMATION:
{detected_key}

ORIGINAL CHORD RECOGNITION RESULTS:
{original_chord_sequence}

BASS NOTE RECOGNITION RESULTS:
{bass_chord_sequence}

Please evaluate the reliability of the bass stem chord recognition results, considering the following factors:
1. Compatibility of the bass stem chords with the detected key
2. Relationship between bass notes and the root/function of the original chords
3. Internal consistency of the bass stem chord recognition
4. Possible error patterns and irregularities

Your goal is to determine whether the bass stem provides reliable bass note information and whether it should be used to revise the bass notes of the original chords.

Please provide a clear YES or NO judgment, followed by a brief explanation:
- YES: The bass stem chord recognition provides valuable bass note information and should be used to correct the original chords
- NO: The bass note recognition is unreliable or does not offer better bass note information than the original chords

Answer format:
DECISION: [YES/NO]
REASONS: [brief explanation]
"""


BASS_REFINEMENT_PROMPT = """
As a music theory expert, refine chord progressions using bass stem information.

CRITICAL REQUIREMENTS:
1. Preserve EXACT timing values - Do not modify timestamps
2. Maintain temporal continuity - Ensure no gaps in timeline
3. Output same number of chords as input

INPUT FORMAT:
- Original chords: <start_time> <end_time> <chord_label>
- Bass notes: <start_time> <end_time> <bass_note>
- Detected key: <key> <confidence>

ORIGINAL CHORD SEQUENCE:
{original_chord_sequence}

BASS NOTE SEQUENCE:
{bass_chord_sequence}

DETECTED KEY:
{detected_key}

PROCESSING RULES:
1. **TIMING PRESERVATION**: Copy start_time and end_time EXACTLY from input (including all decimal places)
2. **TEMPORAL CONTINUITY**: Maintain exact timing relationships, preserve any existing gaps or overlaps exactly
3. **COMPLETE OUTPUT**: Process EVERY chord in input sequence order, output must have identical number of lines
4. **BASS "N" HANDLING**: If bass is "N" at chord's time point, keep original chord UNCHANGED
5. **PRESERVE CHORD QUALITIES**: NEVER change 7th, sus, add, or other chord extensions unless clearly wrong
6. **ORIGINAL "N" CHORDS**: If original chord is "N" but bass has valid note, assign appropriate diatonic chord

REFINEMENT LOGIC for each chord:
- Find bass note that overlaps with chord timing
- If bass = "N" or missing → keep original chord UNCHANGED
- If original chord = "N" but bass has valid note → assign diatonic chord with that bass as root
- If original chord has defined quality:
  - Parse chord: Extract root, quality (including all extensions like 7, sus, add), current inversion
  - If detected bass matches expected bass → keep original chord UNCHANGED
  - If detected bass is different:
    - If new bass is chord tone → update inversion ONLY, preserve ALL chord qualities (7, sus, etc.)
    - If new bass is not chord tone → keep original chord unchanged (avoid changing established harmonies)
  
CRITICAL: Focus ONLY on bass/inversion changes. Preserve ALL chord qualities (maj7, m7, sus4, sus2, add9, etc.) unless original is "N".

INVERSION NOTATION (use interval numbers, NEVER pitch names):
- Root bass: "D:maj" (NO slash notation, NEVER "D:maj/1")
- 3rd bass: "D:maj/3" (NEVER "D:maj/F#")
- 5th bass: "D:maj/5" (NEVER "D:maj/A")
- 7th bass: "D:maj7/7" (NEVER "D:maj7/C#")

OUTPUT REQUIREMENTS:
- Format: <start_time> <end_time> <chord_label>
- ONE chord per line, space-separated values
- Use EXACT same start_time and end_time as input (copy character-by-character)
- Process chords in exact order they appear in input (do NOT reorder by time)
- NO additional text, explanations, comments, or blank lines

Your response must ONLY contain the chord sequence. Start immediately with first chord line, end immediately after last chord line.
"""

# Reference chord reliability prompt
REFERENCE_CHORD_RELIABILITY_PROMPT = """
You are an expert music theorist evaluating the reliability of two different chord recognition results.

I'll provide you with:
1. A primary chord recognition result (our main prediction)
2. A reference chord recognition result (from a different model)
3. The detected key information for this music

DETECTED KEY INFORMATION:
{detected_key}

PRIMARY CHORD RECOGNITION RESULTS:
{primary_chord_sequence}

REFERENCE CHORD RECOGNITION RESULTS:
{reference_chord_sequence}

Your task is to determine whether the reference chord sequence is reliable enough to be used for improving our primary chord sequence.

Please analyze both sequences considering:

1. HARMONIC CONSISTENCY:
   - Which sequence better aligns with the detected key?
   - Are chord progressions musically logical in each sequence?
   - Which sequence has fewer implausible chord transitions?

2. STRUCTURAL COHERENCE:
   - Which sequence has more consistent chord pattern repetitions?
   - Which has more appropriate chord durations for typical music?
   - Is either sequence missing obvious sections or chords?

3. COMPLEMENTARY VALUE:
   - Does the reference sequence provide information missing in the primary?
   - Could the reference sequence help resolve ambiguous areas in the primary?
   - Are there sections where the reference seems more reliable?

4. OVERALL ASSESSMENT:
   - Considering all factors, is the reference sequence reliable enough to inform refinements?
   - Would integrating information from the reference sequence likely improve our final result?

Based on your analysis, respond with ONLY "YES" or "NO" regarding whether we should use the reference sequence to inform our chord refinement process.
"""


KEY_INFORMED_PROMPT = """
You are an expert music theorist refining chord progressions with special attention to chord quality consistency.

INPUTS:
1. Primary chord sequence - Your main source for analysis
2. Detected key information - Provides harmonic context 
3. (Optional) Reference chord sequence - Supporting evidence only

DETECTED KEY INFORMATION:
{detected_key}

PRIMARY CHORD SEQUENCE:
{chord_sequence}

REFERENCE CHORD RECOGNITION RESULTS:
{reference_chord_data}

STRICT PROHIBITIONS (ABSOLUTE - NO EXCEPTIONS):
- DO NOT change bass notes, slash chord notations (e.g., C/E must remain C/E)
- DO NOT modify, remove, or convert sus chords (sus2, sus4, sus4(b7)) to ANY other chord qualities
- NEVER change sus chords even if they seem inconsistent with key or pattern

REFINEMENT APPROACH (by priority):

1. HARMONIC CONTEXT ANALYSIS (HIGHEST PRIORITY):
   Before making chord quality changes, check for functional justification:
   
   a) MODAL INTERCHANGE / BORROWED CHORDS:
      - For minor keys: Check if chord could be borrowed from parallel major
      - For major keys: Check if chord could be borrowed from parallel minor
      - Example: In Eb minor, Eb7 could be borrowed from Eb major - PRESERVE IT
      - Common borrowed chords: bVII, bIII, bVI in major; I, IV in minor
   
   b) SECONDARY DOMINANTS:
      - Check if chord functions as V/X (dominant of following chord)
      - If chord is dominant 7th of next chord's root, it's likely secondary dominant
      - Formula: If chord X is dominant 7th and next chord's root is perfect 5th below X's root
      - Example: If A7 followed by D (major/minor), A7 is V/D - PRESERVE IT
   
   c) When in doubt, preserve original chord quality
   d) Only change if chord clearly contradicts key AND lacks functional justification

2. CHORD QUALITY CONSISTENCY (HIGH PRIORITY):
   - FIRST: Check if ANY occurrence has functional justification (modal interchange, secondary dominant)
   - If any occurrence is functionally justified, preserve ALL variations for that root
   - Only standardize when NO harmonic justification exists for ANY variation
   - Identify all occurrences of same root note and check each individually
   - Use reference data as supporting evidence only, never as primary reason for change

3. PATTERN RECOGNITION (MEDIUM PRIORITY):
   - Identify most frequent 2-3 chord sequence patterns (3+ repetitions)
   - Treat consistent patterns as expected harmonic template
   - Deviations may be intentional for harmonic color - check context first

4. EXECUTION RULES:
   - Preserve all bass notes ("/"), sus designations, inversion information, "N" segments, and timing boundaries
   - DO NOT remove "N" segments even if reference suggests a chord
   - Focus only on chord quality changes that serve consistency without removing harmonic variety
   - Prioritize preserving harmonic variety over strict consistency

Return ONLY the refined chord sequence in format: <start_time> <end_time> <chord>
"""

# Anomaly detection prompt
anomaly_detection_prompt = """
You are an expert music theorist specializing in chord progression analysis. Your task is to examine a chord sequence and identify ONLY the most critical missing/wrong chord information.

I will provide:
1. The estimated chord sequence
2. Key information for the piece with its confidence level

CRITICAL CONSTRAINTS - READ CAREFULLY:

1. ABSOLUTE DEFAULT: The CHORD SEQUENCE is presumed correct
2. ONLY FOCUS ON "N" CHORDS: The issue you should identify is "N" segments in the  CHORD SEQUENCE
3. Igonre the "N" segments with long duration (>5 seconds), it is likely to be a silent part of the song
4. EXAMINE "N" SEGMENTS WITH EXCEPTIONS: Check EACH "N" segment in the CHORD SEQUENCE, BUT IGNORE "N" segments in the first line and last line of the sequence
4. IGNORE ALL OTHER DIFFERENCES: Different chord choices between sequences are NEVER issues, even if they suggest different patterns

COMPREHENSIVE "N" SEGMENT DETECTION:

For EVERY "N" segment in the CHORD SEQUENCE (EXCLUDING first and last lines), flag it as an issue if ANY of these conditions are met:
- The REFERENCE CHORD SEQUENCE shows a clear chord in the same position
- The "N" segment interrupts a clear chord pattern
- The "N" segment is at a structurally important position (middle sections or section boundaries, but NOT start or end of piece)

SPECIAL EXCEPTION RULE:
- DO NOT flag "N" segments that appear in the FIRST LINE or LAST LINE of the chord sequence
- These beginning and ending "N" segments are considered acceptable and should be ignored

For clarity, here is what you SHOULD NOT flag as issues:
- Different chord labels between sequences 
- Different chord timings or durations
- Different chord patterns or progressions
- Any segment that already has a chord label (even if it differs from reference)
- "N" segments in the first line or last line of the sequence
- "N" segments with long duration (>5 seconds)

Your task is to identify ONLY this specific issue:

## MISSING CHORD INFORMATION (ONLY VALID ISSUE TYPE)
- ONLY flag "N" segments in the KEY-REFINED CHORD SEQUENCE where:
  * The segment is substantial 
  * The segment is NOT in the first line or last line
  * The segment is NOT a silent part of the song
  * The REFERENCE CHORD SEQUENCE shows a clear chord in that position
  * The "N" segment interrupts an otherwise clear musical pattern

INPUTS:

KEY-REFINED CHORD SEQUENCE:
{key_refined_sequence}

REFERENCE CHORD SEQUENCE:
{reference_sequence}

DETECTED KEY INFORMATION:
{detected_key}

Output format:
NEEDS_REFINEMENT: [YES/NO]

ISSUES:
1. [Type: MISSING] [Time range: X.XX-X.XX] [Description: "N" segment that should contain a chord based on reference and surrounding context]
2. [Type: MISSING] [Time range: X.XX-X.XX] [Description: "N" segment that should contain a chord based on reference and surrounding context]
...

If no "N" segments require fixing, output:
NEEDS_REFINEMENT: NO
"""

targeted_refinement_prompt = """
As an expert music theorist with deep knowledge of chord progressions and harmony, your task is to perform targeted refinement on a chord sequence that has specific identified issues.

I will provide:
1. The current estimated chord sequence 
2. Reference chord data from another recognition model
3. Key information for the piece with its confidence level
4. A list of specific issues that need addressing

INPUTS:

DETECTED KEY INFORMATION:
{detected_key}

ISSUES TO FIX:
{issues_to_fix}

CURRENT CHORD SEQUENCE:
{key_refined_sequence}

REFERENCE CHORD SEQUENCE:
{reference_sequence}

Your task is to carefully fix ONLY the identified issues while preserving the rest of the sequence exactly as it is.

CRITICAL TIMING RULE:
- NEVER modify, adjust, or change ANY <start_time> or <end_time> values
- All timing boundaries must remain EXACTLY as provided in the input
- Only the chord symbols themselves may be modified, never the timing

HARMONIC CONTEXT CONSIDERATIONS:
Before marking any progression as "unreasonable", consider these common harmonic techniques:
- MODAL INTERCHANGE: Chords borrowed from parallel major/minor keys are common and valid
  * In minor keys: I, IV, bVII from parallel major
  * In major keys: i, iv, bIII, bVI, bVII from parallel minor
- SECONDARY DOMINANTS: V7/X chords that resolve to any diatonic chord
  * If a dominant 7th chord resolves down a perfect 5th, it's likely a secondary dominant
- CHROMATIC MEDIANTS: Non-diatonic chords a third away can be intentional color choices
- EXTENDED HARMONY: Jazz and contemporary music often uses non-diatonic chords intentionally

IMPORTANT REFINEMENT RULES:

1. MISSING CHORD INFORMATION (HIGHEST PRIORITY):
   - Replace "N" segments with appropriate chords ONLY in specific circumstances
   - **PRESERVE "N" in these cases:**
     * **First line (opening) and last line (ending) of the sequence - these often represent silence before/after the music**
     * **Any "N" segment with duration > 8 seconds - these likely represent intentional silent passages or breaks**
   - **Replace "N" segments only when:**
     * They occur in the middle of the sequence (not first or last line)
     * Duration is ≤ 8 seconds
     * There is clear harmonic context from surrounding chords
   - When replacing "N" segments, consider:
     * The surrounding chords and their harmonic function
     * The key context
     * Whether the reference chord would create a sensible progression
   - MAINTAIN the exact <start_time> and <end_time> of the "N" segment
   - **Duration calculation: end_time - start_time**

2. UNREASONABLE PROGRESSIONS (APPLY VERY CONSERVATIVELY):
   - Only correct progressions that are CLEARLY erroneous and have no harmonic justification
   - Before marking a progression as unreasonable, verify it's not:
     * A borrowed chord from the parallel key
     * A secondary dominant or subdominant
     * A chromatic mediant relationship
     * A common jazz/pop substitution
   - Examples of truly unreasonable progressions:
     * Random chromatic chords with no resolution
     * Chords that create persistent dissonance without purpose
     * Progressions that clearly sound like recognition errors
   - When in doubt, PRESERVE the original progression
   - DO NOT merge or split time segments - only change the chord symbol

3. PRESERVATION RULES:
   - DO NOT modify ANY chord or timing outside the specified issues
   - Maintain the original time boundaries exactly - no adjustments to <start_time> or <end_time>
   - Preserve chord quality and inversions unless specifically addressing an issue
   - Maintain the overall harmonic rhythm and structure
   - Each line in the output must have the same <start_time> and <end_time> as the corresponding input line
   - Respect harmonic diversity - don't oversimplify to only diatonic chords

Return ONLY the refined chord sequence in the same format: <start_time> <end_time> <chord>
Each output line must preserve the exact timing from the input sequence.
"""


