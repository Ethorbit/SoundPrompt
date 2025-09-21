<!-- LICENSE HEADER MANAGED BY add-license-header

Copyright (C) 2025 Ethorbit

This file is part of SoundPrompt.

SoundPrompt is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3
of the License, or (at your option) any later version.

SoundPrompt is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the
GNU General Public License along with SoundPrompt.
If not, see <https://www.gnu.org/licenses/>.
-->

# SoundPrompt
## Your sounds, triggered by AI

SoundPrompt is a tool that plays your prerecorded audio files with AI prompts. It can enhance podcasts, live streams, online calls, and pranks / trolling by adding dynamic elements like music, sound effects, and custom audio cues to engage an audience or inject humor.



## Soundboard: a relic of the past!
![Sound Selection Time chart](./resources/sound-selection-time-chart.png)

Using mechanical or software controls to trigger sounds is an unintuitive process that requires practice and scales horribly. SoundPrompt solves these problems by utilizing the power of Artificial Intelligence and modern hardware to play the sounds you want, faster than you ever could.

## Usage

* For each audio file
  * Create a file with the EXACT SAME name, ending with .txt (e.g. epic-explosion.wav.txt)
  * Inside the file, add comma separated tags describing the sound: `explosion, boom`

* Save the library: `python ./src/main.py --save <directory>`

* Load the library: `python ./src/main.py --load <directory>`

* After loading, type something that resembles the sound you want to hear (e.g. explode)

### 🎤 Routing to Your Apps
SoundPrompt does not create a virtual microphone. It simply plays sounds through the device's primary output device.
To use it in apps like Discord, Zoom, OBS, etc, you’ll need a **virtual audio cable/loopback** to route the sound as if it were a mic.

<details>
<summary>Windows</summary>

- Install [VB-Cable Free](https://vb-audio.com/Cable/) (single virtual cable).  
- Set SoundPrompt’s output to *VB-Cable Input*.  
- In Discord (or any other app), select *VB-Cable Output* as your microphone.

</details>

<details>
<summary>macOS</summary>

- Use [BlackHole](https://github.com/ExistentialAudio/BlackHole) (free, open-source).  
- Route SoundPrompt through the virtual device.  
- Choose that virtual device as the input in your app.  

</details>

<details>
<summary>Linux</summary>

- Use **PulseAudio** (usually preinstalled) or **JACK** (optional advanced routing).  
- With `pavucontrol`, create a loopback from SoundPrompt’s output to a virtual input.  
- Select the virtual input as your microphone in the target app.  

</details>
