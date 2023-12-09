# AbraTools Beta
### *AbraTools contains a list of many quality-of-life animation tools for Blender. It's made by animators, for animators.*

**Code is a mess. Be careful using it in production. Bug reports, feature requests and PRs are appreciated.**

* Working as of Blender 4.0.1.
* Known bugs in 3.6+:
  * **Isolate Curves**: Due to an internal change with keymapping funcionality, Isolate Curves can only be triggered by double-clicking inside of the channel box, instead of releasing left-click.
* **Download** AbraTools [here](https://github.com/abrasic/abratools/releases). 
* **Installation instructions** [here](https://docs.abx.gg/support/download-and-setup). 
* **Read the docs** [here](https://docs.abx.gg).

## ⚠️ IMPORTANT: If you're downloading from the repository directly, understand its consequences.
It's advised that you download from [RELEASES](https://github.com/abrasic/abratools/releases) instead of the REPOSITRORY. If you so choose to receive the latest code changes to abraTools please understand the following:

* I test all new code on professional animation workspaces. Most testing is extensive, but that doesn't mean new code and tools are prone to errors.
* I give no support for any revision of abraTools that you download directly from the repository (ex. using the "Code > Download ZIP" button).
* **We are not responsible for any disruptions, crashes, data loss, and all other undetermined actions caused by cutting-edge versions of abraTools. It is your responsibility to create back-up files. You should however, [report these indicents](https://github.com/abrasic/abratools/issues/new) whenever they happen.**
# SETUP
![openshelf](https://user-images.githubusercontent.com/43157991/235394650-f7f58f6c-11dc-4121-bfa9-5841d166756c.gif)

You can open the abraTools toolshelf by simply clicking the icon located in the header of the 3D viewport. If you ever want to make changes to how your toolshelf looks, you can expand it to access the visibility options.

# TOOLS
## Customization
> Control how you want your toolshelf to look and hide tools you dont want to see. Everything is hotkeyable, too!
<img src='https://user-images.githubusercontent.com/43157991/186026209-27349ba2-0c03-470c-8eb3-bd804ccf043f.gif' height='225'>

## Isolate Curves
> Automatically hide F-Curves that aren't selected. Bye-bye, `Shift+H`!
<img src='https://1352856054-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FVEvUhh6zNMLIFbTZCBjF%2Fuploads%2FB98EYtCW0t2zu5VVcmc5%2Fisolate_curves.gif?alt=media&token=666c8e89-8091-45f0-a795-c76f662997e2' height='325'>

## Auto Frame
> Quit panning around the graph editor as much to find your F-Curves. AbraTools will automatically frame F-Curves into view for your current frame range.

![auto_frame](https://user-images.githubusercontent.com/43157991/215243104-d9e246fd-d26c-42b6-af0a-a6b37a1a45da.gif)

## Smart Keyframe Jumping
> Navigate between keys faster with smart keyframe jumping and automatic selection

![smartselect](https://github.com/abrasic/abratools/assets/43157991/8bb918fb-6a22-47c7-b121-30844906596e)


## Quick Motion Path Setup
> Avoid the tedious work of setting up motion paths. One click and you're ready to rock.

<img src='https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FVEvUhh6zNMLIFbTZCBjF%2Fuploads%2F1C7hZSEIhrmpW1sHYghV%2Fmopath.gif?alt=media&token=313e0db0-3328-494d-a0e7-5ec12ecf65f3' height='325'>

## Quick View Curves
Quickly see the curves that matter to you most.

<img src='https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FVEvUhh6zNMLIFbTZCBjF%2Fuploads%2FKnF0CEtxUrFmDJp4O8Ej%2Fquickview.gif?alt=media&token=b1ffa007-3337-41f8-afa1-5918359b3d5c' height='325'>

## Key All Shape Keys
> Quickly block out your shapes. Avoid constant [I] key spam.

<img src='https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FVEvUhh6zNMLIFbTZCBjF%2Fuploads%2F3rp1IS8hBvS8cJotKr2Z%2Fkeyallshapes.gif?alt=media&token=00bc591e-4632-4c11-8537-35650599bfbf' height='325'>

## Key Whole Armature
> Block entire rigs faster.

<img src='https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FVEvUhh6zNMLIFbTZCBjF%2Fuploads%2FE1UnPXeSTYNLz69Jk1iJ%2Fkeyarmature.gif?alt=media&token=d0d768c4-8ed4-4fea-a66d-701bccc3f8a6' height='325'>

## Retime Scene
> Need more space in a moving hold without the fear of screwing up your timing in other shots? We got you covered. Our retime feature moves camera markers and all other keyframes in your scene automatically.

![retime](https://user-images.githubusercontent.com/43157991/209421291-2373a142-1e5c-42a4-a923-b7ea82f20967.gif)

## Bake Keys
> Bake some keys on ones, twos, or whatever interval you prefer.

![bake](https://user-images.githubusercontent.com/43157991/213976577-f5155bcc-649b-49da-ad10-76bc8f29e542.gif)


## Selection Sets+
> Access and manage your selection sets quicker.

<img src='https://user-images.githubusercontent.com/43157991/186025824-a90eef9a-f857-4663-9958-14a4a4791b10.gif' height='325'>

## Quick Pivot
> Quickly change your pivot point using the 3D cursor.

<img src='https://user-images.githubusercontent.com/43157991/186027819-cf7afa6d-655d-4f82-8001-c08864ac87d5.gif'>


## Quick Copy/Paste

> Copy keys on the playhead and use it for another time.

<img src='https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FVEvUhh6zNMLIFbTZCBjF%2Fuploads%2FiFOCL2B09nS2NMmJNlJu%2Fcopypaste.gif?alt=media&token=f6973c0a-c066-4516-ae0a-826fc68da871' height='325'>

## Custom Scripts

> Create your own Python scripts and use them on the toolshelf

[Learn more](https://docs.abx.gg/feature/custom-scripts)

![custom](https://github.com/abrasic/abratools/assets/43157991/fb7cbba9-efa3-4694-b570-8ac33af606cd)


**Plus ~~many~~ a few more.**
