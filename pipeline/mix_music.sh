#!/usr/bin/env bash
# Mix the Ep 02 music beds under a finished render (no re-render needed) and normalise loudness.
# Usage: bash tools/mix_music.sh IN.mp4 OUT.mp4 [NIGHT_DB] [DAY_DB] [TARGET_I] [STINGER.mp3] [STINGER_DB]
# Optional stinger: a short hit placed exactly on the "போதும்." cut (20.37 s), faded out before the narrator's "Okay." (21.02 s), not ducked.
# Night bed: 0 s -> hard stop at the "போதும்." turn (20.37 s). Day bed: from 21.81 s to the end, 1.7 s fade out.
# The beds duck under the voice + effects mix (sidechain compression).
set -euo pipefail
in="${1:?in.mp4}"; out="${2:?out.mp4}"; nd="${3:--16}"; dd="${4:--17}"; ti="${5:--15.3}"; sting="${6:-}"; sg="${7:--6}"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
dlen=$(echo "$dur - 21.81" | bc); dfo=$(echo "$dlen - 1.7" | bc)
if [ -n "$sting" ]; then
  extra_in=(-i "$sting")
  st="[3:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:1.0,afade=t=out:st=0.55:d=0.45,volume=${sg}dB,adelay=20370:all=1[st];"
  final="[v][md][st]amix=inputs=3:normalize=0:duration=first"
else
  extra_in=(); st=""; final="[v][md]amix=inputs=2:normalize=0:duration=first"
fi
ffmpeg -v error -y -i "$in" -i voice/ep02_music/night.mp3 -i voice/ep02_music/day.mp3 "${extra_in[@]}" -filter_complex "${st}\
[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:20.37,afade=t=in:st=0:d=0.3,afade=t=out:st=20.31:d=0.06,volume=${nd}dB[n];\
[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:${dlen},afade=t=in:st=0:d=0.8,afade=t=out:st=${dfo}:d=1.7,volume=${dd}dB,adelay=21810:all=1[d];\
[n][d]amix=inputs=2:normalize=0:duration=longest[m];\
[0:a]aformat=channel_layouts=stereo,asplit=2[v][sc];\
[m][sc]sidechaincompress=threshold=0.035:ratio=4:attack=15:release=350[md];\
${final},loudnorm=I=${ti}:TP=-1.5:LRA=11,alimiter=limit=0.84[out]" \
  -map 0:v -map "[out]" -c:v copy -c:a aac -b:a 192k -ar 48000 "$out"
lufs=$(ffmpeg -v info -i "$out" -af ebur128=framelog=quiet -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}')
echo "wrote $out · ${lufs} LUFS (target -14.5 ± 0.5)"
