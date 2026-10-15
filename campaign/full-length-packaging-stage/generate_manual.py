#!/usr/bin/env python3
"""Editable full-campaign booklet generator; writes only its own staging folder."""
from pathlib import Path
from hashlib import sha256
import html
import os
import json
import shutil
from xml.sax.saxutils import escape
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image as PDFImage

STAGE=Path(__file__).resolve().parent
ROOT=STAGE.parents[1]
OUTPUT=STAGE/'output/pdf'
ASSETS=STAGE/'assets'
FONT_ROOT=Path(os.environ.get('STARFALL_MANUAL_FONT_DIR', str(STAGE/'fonts')))
if not all((FONT_ROOT/name).is_file() for name in ('DejaVuSans.ttf','DejaVuSans-Bold.ttf')):
    raise SystemExit('Set STARFALL_MANUAL_FONT_DIR to a directory containing DejaVuSans.ttf and DejaVuSans-Bold.ttf.')
W,H=letter
INK=colors.HexColor('#152D42');TEAL=colors.HexColor('#08787D');PAPER=colors.HexColor('#FAF9F2')
GOLD=colors.HexColor('#C79135');MUTED=colors.HexColor('#556779')
ZONES=['Wreck Hull','Coolant Works','Solar Foundry','Signal Archive','Outer Array','Star Engine']
INPUTS={}
VERSION='1.2'
DOCS_REVISION='2026-10-14'
# Frozen ROM identity; replace summaries only after final evidence is accepted.
# main() refuses to generate deliverables while any value remains TODO.
NATIVE_ROM_SHA256='da88897984d4ead183a8e14aa9c7dcea91592445e27a9cd62517cba432f83a78'
NATIVE_QUALIFICATION=(
    '<b>Native 1.2 functional pass:</b> 18 missions, 72 rooms, 18 guardians and seven rescues; clear time <b>31:26, Rank B</b>. '
    'One M17 escort failure recovered through ordinary Retry. '
    'All 12 Arcade sectors passed without retry and banked 22,500. '
    'Same-session Title/Continue restored committed Story stages and the ending, including after Arcade banking. '
    'This does not test native cold-start save persistence.'
)
BROWSER_QUALIFICATION=(
    '<b>Browser 1.2 checks:</b> two Story missions/eight rooms plus one Arcade sector passed, including retry and checkpoint Continue after failed attempts. '
    'Change Rig then Back kept the rig; direct launch and Pause were exercised. '
    'Banking 300 survived ordinary reload, which also restored Story M03 Bay 1 at full hull. '
    'Reload checked 1.1-to-1.2 continuation and earned route/mission checkpoints. '
    'Coverage is limited to those rooms; no full browser clear time or complete Arcade cycle is claimed. '
    'Same-session SRAM recovery differs from persisted browser reload; native cold-start saves remain unverified.'
)


def digest(path):return sha256(path.read_bytes()).hexdigest()
def retain(source,name):
    source=ROOT/source;target=ASSETS/name
    INPUTS[str(source.relative_to(ROOT))]=digest(source)
    shutil.copyfile(source,target)
    return name


def paragraph(text):return ('p',text)
def heading(text):return ('h',text)
def box(text):return ('box',text)
def table(headers,rows,widths):return ('table',headers,rows,widths)
def picture(name,width,caption):return ('image',name,width,caption)
def pictures(items):return ('images',items)

def screenshot(name):
    path=ASSETS/'screenshots'/name
    manifest=json.loads((ASSETS/'screenshots/SCREENSHOTS.json').read_text())
    assert manifest['nativeRomSha256']==NATIVE_ROM_SHA256, 'Screenshot ROM differs from manual version'
    entries=manifest['screenshots']
    entry=next(item for item in entries if Path(item['file']).name == name)
    assert digest(path)==entry['sha256'], f'Screenshot hash mismatch: {name}'
    assert Image.open(path).size==(160,144), f'Unexpected screenshot size: {name}'
    INPUTS[str(path.relative_to(ROOT))]=digest(path)
    return 'screenshots/'+name


def content():
    missions=[json.loads((ROOT/f'campaign/mission-{n:02d}.json').read_text()) for n in range(1,19)]
    for n in range(1,19):
        path=ROOT/f'campaign/mission-{n:02d}.json';INPUTS[str(path.relative_to(ROOT))]=digest(path)
    assert len(missions)==18 and sum(len(m['rooms']) for m in missions)==72
    title=screenshot('title-1.2.png')
    escort=screenshot('escort-flight.png')
    guardian=screenshot('guardian-core-open.png')
    route=screenshot('route-choice.png')
    pause=screenshot('pause-menu.png')
    workbench=screenshot('workbench.png')
    bank_choice=screenshot('arcade-bank-choice.png')
    bank_result=screenshot('arcade-bank-result.png')
    ending=screenshot('story-ending-1.2.png')
    INPUTS[str((ASSETS/'screenshots/SCREENSHOTS.json').relative_to(ROOT))]=digest(ASSETS/'screenshots/SCREENSHOTS.json')
    retain(Path('artwork/box-art.png'),'box-art.png')
    source_rows=[]
    for index,m in enumerate(missions):
        source_rows.append([f'{index+1:02d}',ZONES[index//3],m['name'].title(), 'Final job' if index%3==2 else 'Regular job'])
    return [
      ('Welcome aboard',[
        paragraph('An original Game Boy Color adventure by <b>Stephan Arrington</b>. Pilot a salvage astronaut through a damaged station: thrust, drift, brake, restore its systems and bring the recovered cargo home.'),
        box('<b>Explore the full campaign:</b> 18 missions across six zones, with 72 large scrolling rooms, plus a separate repeating 12-room Arcade route. Choose your jobs, build a route and bring the salvage home.'),
        heading('Your first flight'),
        paragraph('<b>1. Choose Story.</b> At the title use Up/Down to highlight Story or Continue, then A to confirm. Select Arcade the same way. B goes back or cancels where a previous screen exists; it has no action at the title.'),
        paragraph('<b>2. Choose a job and rig.</b> Up/Down selects a mission; Left/Right selects an unlocked pulse rig.'),
        paragraph('<b>3. Read the objective before launch.</b> The flight deck and next-bay cards show the task. A launches directly from those cards. Initial Arcade, retry and restored launch checkpoints may show READY TO FLY; press A there to begin. Start opens Pause for objective help.'),
        paragraph('<b>4. Fly the objective.</b> Tap a direction to gain momentum. Release to drift; hold B to brake. Press A for a ready close-range pulse.'),
        paragraph('<b>5. Deliver.</b> After completing the objective, return beside the real dock terminal. Delivery is automatic. In large rooms the dock is a specific safe area, not the entire bottom edge.'),
        picture(title,160,'Native 1.2 emulator capture: Up/Down chooses a mode and A begins. Ship, stars and exhaust animate while the title theme plays; there is no intro to wait through.'),
      ]),
      ('Controls and drift',[
        table(['Handheld','Browser default','Action'],[
          ['D-pad','Arrow keys','Thrust in play; Up/Down chooses in menus'],['A','Z','Pulse in play; confirm selection in menus'],
          ['B','X','Brake/interact in play; back/cancel in menus'],
          ['Start','Enter','Pause and resume'],
          ['Select','P / Shift','Open exit options during play'],
        ],[58,88,202]),
        paragraph('Browser keys match the supplied game export. Click the game area to focus it, or use the on-screen controller. Follow the displayed controls if you choose a different emulator or remap its keys.'),
        heading('Make momentum work for you'),
        paragraph('Thrust builds speed rather than moving your astronaut instantly. Releasing the D-pad leaves a drift. Start braking <b>before</b> a corner, then steer out of it. B also permits slower, more precise movement while held.'),
        paragraph('A pulse checks nearby enemies when you press A. Watch <b>A READY / A WAIT</b>; holding A does not repeatedly fire. Keep enough space to evade before spending a pulse.'),
        heading('Read the HUD'),
        paragraph('<b>H</b> is your hull, initially three points. The objective counter tracks cargo or nodes; in escort rooms <b>R</b> shows crew hull. M is the mission and BAY is the room within that mission. Direction hints point toward the next target, crew route or dock.'),
        box('Give a new card a moment to settle, then release and press the intended button. After launch, release and press A again to pulse. Held directions and B work as soon as play resumes.'),
      ]),
      ('Salvage, relays and repair',[
        heading('Salvage: approach all three'),
        paragraph('Cells, shards and beacons collect automatically when your astronaut drifts within their close range. Recover all three, then return beside the dock terminal. Merely approaching the dock before the objective is complete does not clear the room.'),
        heading('Ordered relays: the flashing node'),
        paragraph('Find the currently flashing node and hold <b>B continuously for 30 eligible gameplay updates</b> while within 12 pixels. Activate the three nodes in their indicated order. The HUD shows NODE and the current hold count.'),
        paragraph('Releasing B or leaving the active node resets its partial hold. Another node cannot be activated early. Once all three are online, return to the dock.'),
        heading('Repair: any unfinished station'),
        paragraph('Hold <b>B continuously for 45 eligible gameplay updates</b> within 12 pixels of an unfinished station. Repair all three in any order, then dock. You can choose the station order that gives the safest route around the enemy.'),
        paragraph('Release B, move away, or switch to another station and the partial hold resets. Completed stations remain completed within that attempt. Paused time does not advance these counters.'),
        table(['Interaction','Required hold','Order'],[
          ['Relay','30 eligible updates','Flashing node only'],
          ['Repair','45 eligible updates','Any unfinished station'],
          ['Optional gold cache','20 eligible updates','One mission badge'],
        ],[121,121,106]),
        box('These counts are gameplay updates, not a promise about wall-clock time on every emulator or device. Brake beside the station and read the live HUD.'),
      ]),
      ('Crew and guardian encounters',[
        heading('Escort: stay close, then bring both home'),
        paragraph('The crew is a physical actor with <b>two hull points</b>. It follows its authored route only while you remain within <b>24 pixels</b>. Moving farther away stops it. Stay nearby to guide it through all three real route markers.'),
        paragraph('Enemy charges and active floor hazards can hurt the crew. Defend it with a ready pulse and use cover. To wait before a dangerous crossing, move out of follow range while the crew is still on safe floor, then regroup when the route clears.'),
        paragraph('The third marker alone is insufficient. The crew must finish its full route at the dock, and <b>your astronaut must also return beside the terminal</b> to deliver. Losing the crew ends the attempt; retry restores it.'),
        heading('Guardian: three separate openings'),
        paragraph('Every mission ends with a guardian that has <b>three shield points</b>. Evade its committed dash, then close in while the HUD says <b>CORE OPEN</b>. A pulse within your rig radius removes one point, at most once per opening.'),
        paragraph('Pulsing outside OPEN can stun the guardian but does not damage its shield. After the third successful hit it releases three collectible cores: recover them and dock to finish the mission.'),
        pictures([(escort,'Native 1.2 emulator capture: the crew follows your astronaut through the room.'),(guardian,'Native 1.2 emulator capture: CORE OPEN - A PULSE marks the guardian damage window.')]),
      ]),
      ('Enemies, hazards and safe docks',[
        table(['Threat','Read it','Your response'],[
          ['Charger','Amber locks a straight dash','Leave the aimed line; return during recovery'],
          ['Sweeper','Locks one horizontal or vertical axis','Cross its locked axis; use solid cover'],
          ['Hunter','Moves between dashes; targets crew in escort','Keep space and protect the crew route'],
        ],[64,125,159]),
        paragraph('A drone damages actors during its <b>red charge</b>. Amber warning, ordinary recovery and cyan stun are approach windows. A charge can stop against solid cover. In a guardian room, use the explicit CORE OPEN status for damage opportunities.'),
        heading('Floor colors are a clock'),
        paragraph('Dim vent or beam markings are safe. <b>Amber warns; red is active and damaging.</b> Floor cycles begin after the first completed objective marker, or at launch for a guardian. Wait on safe floor rather than drifting into a red lane.'),
        paragraph('Your pulse affects the enemy. It does not turn off floor hazards. The mission power-route perk can disable the second middle room\'s hazard before you enter it.'),
        heading('The dock protects; the room still matters'),
        paragraph('In Story, only the area beside the actual terminal is the safe dock. The classic small Arcade maps use their bottom dock strip. Stay near the terminal when delivering; the lower edge of a scrolling room is not a universal safe lane.'),
        paragraph('Your astronaut and the crew briefly resist repeat damage after a hit. At zero astronaut hull, or zero crew hull in escort, the room attempt fails.'),
        box('Story repairs your astronaut to three hull points on room entry, retry and successful delivery. Earlier completed rooms and the current mission route are kept when you retry.'),
      ]),
      ('Pulse rigs and route choices',[
        table(['Rig','Radius','Reload','Stun','Tradeoff'],[
          ['Standard','24 px','120','60','Balanced default'],
          ['Fast Capacitor','20 px','72','30','More shots; closer range and shorter stun'],
          ['Wide Coil','36 px','180','60','Reach farther; wait longer'],
          ['Overcharge','24 px','180','90','Longer stun; wait longer'],
        ],[83,42,43,40,140]),
        paragraph('Reload and stun are eligible gameplay updates. At an ideal 60 updates per second, 120 is about two seconds. Rigs <b>replace</b> one another; they do not stack. A guardian still allows only one shield hit per opening.'),
        table(['Unlock','First mission clear'],[
          ['Wide Coil','01 - Salvage Signal'],['Fast Capacitor','02 - Bulkhead Circuit'],
          ['Overcharge','09 - Heat Grid'],
        ],[115,233]),
        heading('Choose which middle room comes first'),
        paragraph('After the arrival room, choose <b>REPAIR FIRST</b> or <b>RELAYS FIRST</b> to take the power route, or <b>CREW FIRST</b> or <b>TOOLS FIRST</b> for supply. Up/Down selects; A launches directly. Power first disables the hazard in the other middle bay after power is complete.'),
        paragraph('Taking the <b>supply route first</b> shortens pulse reload in the power route to at most 72 updates. The selected rig\'s radius and stun remain unchanged. You must complete both routes before the guardian. B returns to the title with the checkpoint retained.'),
        paragraph('Flight-deck Left/Right selects unlocked rigs. Arcade CHANGE RIG is optional: Up/Down selects, A fits the rig and flies onward, and B returns to the dock without applying a choice.'),
        picture(route,144,'Native 1.2 route choice: the highlighted card shows the benefit for the other middle bay. Both bays must be cleared.'),
      ]),
      ('Six zones, eighteen jobs',[
        paragraph('In each zone, its <b>two regular jobs may be chosen in either order</b>. Clear both to unlock its final job. Clearing that third job opens the next zone. Each job has four large rooms: arrival, both middle routes, then guardian and extraction.'),
        table(['Job','Zone','Mission','Access'],source_rows,[28,92,151,77]),
        heading('Mission salvage score and caches'),
        paragraph('First-clearing a mission awards 300 salvage; replaying it awards no extra credit. Salvage is not spent in a shop. After MISSION COMPLETE, A opens the flight deck on an available unfinished job; A launches it, or change the selection first. Cleared jobs remain available for replay.'),
        paragraph('Gold cache pads award one optional badge per mission after B is held nearby for 20 updates. The badge is committed at the next confirmed checkpoint. Caches are bonus challenges, not prerequisites for access.'),
      ]),
      ('Pause, retry and checkpoints',[
        heading('Pause and retry'),
        paragraph('<b>Start:</b> pause or resume. Pause repeats the current objective. Up/Down chooses Resume, Retry Room or Exit to Title; A confirms. B resumes without resetting the attempt. Retry Room restarts the current room with full hull and crew, keeping earlier completed rooms and the rig. A at failure retries; B goes back to the title.'),
        paragraph('<b>Select during play:</b> open abandon confirmation. A exits to the title; B cancels into Pause. In Arcade, selecting Fresh Sortie and confirming A loses the unbanked haul. B never selects Retry or Fresh Sortie.'),
        picture(pause,160,'Native 1.2 emulator capture: Up/Down selects a pause option. A confirms it; B resumes the current attempt.'),
        heading('Story saves to cartridge SRAM'),
        paragraph('Story writes a checkpoint on accepted room entry and after completed rooms, branch choices and mission results. The saved card stage, rig, route progress, mission clears, score and campaign statistics can be restored by <b>selecting Continue and pressing A</b> at the title.'),
        paragraph('Continue restores the saved stage: flight deck, route choice, result, mission completion, ending or room-entry briefing. It does not save mid-room position or partial holds. CHECKPOINT SAVED appears on retained entry briefings. <b>SAVE WRITE FAILED</b> means the write was not confirmed; do not assume progress persisted.'),
        heading('New Story and global achievements'),
        paragraph('With a Story checkpoint present, <b>select New Story at the title and press A</b>. A confirms the reset; B cancels. New Story resets campaign progress, mission salvage score, clear-time counters and current rig. Global optional badges, unlocked rigs and best banked Arcade score are retained.'),
      ]),
      ('Arcade: risk another sector or bank',[
        paragraph('Arcade is a separate repeating route through the <b>12 classic small maps</b>, including its Warden. Start with three hull and Standard. Hull carries between sectors; each successful dock repairs one point, up to three.'),
        table(['At the dock','Choice'],[
          ['Fly On - default','A starts the next sector with the current rig'],
          ['Change Rig - optional','Choose Keep Current or an offer; A fits and flies'],
          ['Bank Haul','Select with Up/Down and A to secure the haul'],
          ['B - Back / Exit','Rig screen returns to dock; dock opens exit options'],
        ],[135,213]),
        paragraph('CHANGE RIG defaults to <b>KEEP CURRENT</b>. Offers rotate among Standard, Fast Capacitor, Wide Coil, Overcharge and <b>Hull Patch</b>. Short descriptions show each tradeoff. Hull Patch fully repairs the hull and resets the pulse to Standard. Rigs do not stack.'),
        pictures([(bank_choice,'Native 1.2 dock: Bank Haul is selected here. Fly On is the default choice; Change Rig is optional.'),(workbench,'Native 1.2 rig choice: A fits and flies; B returns to the dock without applying a choice.')]),
      ]),
      ('Complete, bank and return',[
        heading('Earn, bank, lose'),
        paragraph('Completed dock deliveries award 300 in sector 1, 600 in sector 2, and so on up to 3,000 per sector from sector 10. The haul caps at 60,000. Pickups without delivery do not award score.'),
        paragraph('At zero hull the <b>entire unbanked haul is lost</b>. Returning to the title or restarting also abandons that haul. Later loops increase enemy pressure and later sectors shorten safe floor windows. Sector numbers stop increasing at 99 while the route continues.'),
        paragraph('<b>BEST BANKED</b> is saved to cartridge SRAM when you bank. Banking updates Arcade statistics while retaining the committed Story checkpoint. An unfinished sortie has no persistent resume point.'),
        heading('Story: bring the station home'),
        paragraph('Clear all 18 missions and 72 rooms to reach STARFALL SAVED. The ending shows your CLEAR TIME and rank. A or B returns to the title; Continue restores the completed campaign.'),
        pictures([(bank_result,'Native 1.2 Arcade result: the banking card reports the secured haul and best banked score.'),(ending,'Native 1.2 Story ending: STARFALL SAVED reports the completed campaign, clear time and rank.')]),
        box('Banking early is a successful choice. A large haul that never reaches a bank is still unbanked cargo.'),
      ]),
      ('Choose how to play',[
        paragraph('Use <b>Starfall-Salvage-1.2.gbc</b> from the full-game package. This is a <b>Game Boy Color-only</b> game. Original Game Boy and Game Boy Pocket are unsupported. Keep the .gbc extension; this is not a .gba game.'),
        heading('1. Play a separately supplied browser edition'),
        paragraph('Choose <b>Play in Browser</b> at <a href="https://starfall.steph4n.dev" color="#08787D">starfall.steph4n.dev</a>, then click the game area for keyboard focus. Browser files and editable source are separate from the native player ZIP. For a local browser export, extract and serve its folder with a web server, then open its index.html through that server; opening the file directly may not work. Use the controls on page 3 or the on-screen controller. See the <a href="https://www.gbstudio.dev/docs/build/" color="#08787D">GB Studio web-build guide</a>.'),
        heading('2. Open the ROM in a GBC emulator'),
        paragraph('Open the .gbc file in an emulator that supports Game Boy Color and battery saves. Select CGB or automatic color detection, and allow it to save your progress. <a href="https://sameboy.github.io/" color="#08787D">SameBoy</a> is one example; its <a href="https://sameboy.github.io/features/" color="#08787D">documented features</a> include both. This release has not yet been tested in SameBoy.'),
        heading('3. Use a compatible SD flash cartridge'),
        paragraph('The owner confirmed successful <b>version 1.2 play on a Chromatic with an SD flash cartridge</b>. For other setups, use a compatible GB/GBC SD cartridge and color-capable handheld. The EverDrive GB X7 is one example; the owner report does not identify a cartridge model. Power off the handheld, remove the card and connect it to a computer using an ordinary SD-card reader. Copy the .gbc file into a games folder outside the cartridge system folder. Eject the card, reinsert it, power on and choose the game from the cartridge menu. Follow that cartridge\'s manual for saving.'),
        heading('4. Program a writable homebrew cartridge'),
        paragraph('Advanced users can program a compatible writable cartridge using its matching writer and software. Confirm the requirements below, follow the cartridge and writer instructions, and verify the written ROM before use. Different cartridge designs need different writers and settings; a blank cartridge alone is not enough. See this <a href="https://github.com/MouseBiteLabs/Game-Boy-MBC5-Cartridge" color="#08787D">MBC5 cartridge design and writer documentation</a> for an example, not a tested hardware recommendation.'),
        box('<b>Advanced cartridge requirements:</b> MBC5; at least 1 MiB of ROM storage; 32 KiB of persistent save RAM. The supplied ROM header is 0x1E (MBC5 + rumble + RAM + battery). Confirm the exact cartridge/writer combination supports this image. SD copying uses a card reader; Chromatic USB is not an SD-card passthrough.'),
      ]),
      ('Saves, clear time and tested scope',[
        heading('Keep the matching save data'),
        paragraph('Before upgrading from 1.1, <b>back up the existing ROM and battery save</b>. Use your emulator or cartridge\'s normal import/export or save-association process to give a copy of that save to <b>Starfall-Salvage-1.2.gbc</b>. Some setups match saves by ROM basename; a new filename does not automatically migrate the old save.'),
        paragraph('Keep the original backup until Continue restores the expected checkpoint and your setup successfully saves and reopens it. A checkpoint is not a mid-room position. Browser storage belongs to its browser and site address. Native save files and browser storage are managed by their respective emulator or runtime.'),
        heading('Clear time and rank'),
        paragraph('CLEAR TIME counts successful room attempts; it excludes pauses, menus and failed room attempts. It is not a measure of first-time human campaign duration. Rank counts damage to your astronaut, including failed attempts: <b>S</b> for no hits, <b>A</b> for one or two, and <b>B</b> for three or more.'),
        box(NATIVE_QUALIFICATION),
        paragraph(BROWSER_QUALIFICATION),
        paragraph('<b>Owner-confirmed hardware:</b> version 1.2 worked on the owner\'s Chromatic with an SD flash cartridge. This records successful play on that setup; independent hardware validation, other setups and power-off save persistence remain separate checks.'),
        paragraph('<b>Still to verify:</b> independent hardware validation and additional handheld/cartridge setups, heard speaker/headphone audio, native cold-start and power-off saves, full browser close/reopen or crash recovery, other browser/origin configurations and uncoached human enjoyment. Clear-time figures describe the identified build and test, not first-time human duration.'),
      ]),
      ('Credits and flight checklist',[
        heading('Original homebrew by Stephan Arrington'),
        paragraph('Game design, campaign and Arcade implementation, native project development and this booklet: <b>Stephan Arrington with OpenAI Codex assistance</b>.'),
        paragraph('Astronaut, cells, drone, pulse, native room and interface pixel artwork: original artwork authored for Starfall Salvage. Music and sound effects: original chiptune composition, zone arrangements, wave data and gameplay sound-effect code authored for this game.'),
        paragraph('Illustrated box art: AI-generated with the built-in image generation tool. The original illustration and prompt provenance are retained in the project\'s artwork folder. The nine gameplay screenshots in this booklet are unaltered 160 x 144 captures from the version 1.2 native emulator. They are not physical Chromatic photographs or captures. Their source-frame and ROM provenance is retained with the manual assets.'),
        paragraph('Built with <b>GB Studio</b> by Chris Maltby and contributors, and <b>GBDK-2020</b> by the GBDK contributors. Retained project UI/font resources and third-party license notices remain with the <a href="https://github.com/steph4n-gh/starfall-salvage" color="#08787D">source project on GitHub</a>. This booklet does not replace those notices.'),
        heading('Before the next launch'),
        table(['Check','Why'],[
          ['Read the objective','Check the launch/dock card or Pause reminder'],
          ['Know where the real dock is','Delivery requires the terminal\'s safe area'],
          ['Watch A READY / A WAIT','Use a pulse you actually have'],
          ['Brake before turning','Keep the drift under control'],
          ['Give the crew time and space','Three markers plus full dock arrival'],
          ['Keep a backup save','Continue restores the committed checkpoint'],
        ],[140,208]),
        box('<b>Make the next run yours.</b> Try a different middle-room order, discover every cache, master a new pulse rig or bank a bigger Arcade haul. Bring the crew home and keep the station flying.'),
      ]),
    ]


def styles():
    pdfmetrics.registerFont(TTFont('ManualSans',str(FONT_ROOT/'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('ManualBold',str(FONT_ROOT/'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFontFamily('ManualSans',normal='ManualSans',bold='ManualBold')
    return {
      'title':ParagraphStyle('title',fontName='ManualBold',fontSize=23,leading=28,textColor=INK,spaceAfter=16),
      'h':ParagraphStyle('h',fontName='ManualBold',fontSize=13,leading=17,textColor=TEAL,spaceBefore=11,spaceAfter=6),
      'p':ParagraphStyle('p',fontName='ManualSans',fontSize=11,leading=16,textColor=INK,spaceAfter=9),
      'caption':ParagraphStyle('caption',fontName='ManualSans',fontSize=8.5,leading=12,textColor=MUTED,spaceBefore=6,spaceAfter=8),
      'table':ParagraphStyle('table',fontName='ManualSans',fontSize=9.5,leading=13,textColor=INK),
      'tablehead':ParagraphStyle('tablehead',fontName='ManualBold',fontSize=9.5,leading=13,textColor=colors.white),
      'box':ParagraphStyle('box',fontName='ManualSans',fontSize=10,leading=15,textColor=INK),
    }


def page_background(canvas,doc):
    canvas.saveState();canvas.setFillColor(PAPER);canvas.rect(0,0,W,H,fill=1,stroke=0)
    canvas.setStrokeColor(GOLD);canvas.setLineWidth(1);canvas.line(34,H-33,W-34,H-33)
    canvas.setFillColor(MUTED);canvas.setFont('ManualBold',8)
    canvas.drawString(34,H-24,'STARFALL SALVAGE / FLIGHT MANUAL')
    canvas.drawRightString(W-34,H-24,'VERSION 1.2 / 2026-10-14')
    canvas.setLineWidth(.4);canvas.setStrokeColor(colors.HexColor('#C8D2D3'));canvas.line(34,33,W-34,33)
    canvas.setFont('ManualSans',8);canvas.drawString(34,21,'Full Campaign Flight Manual 1.2 | Stephan Arrington')
    canvas.drawRightString(W-34,21,f'{doc.page:02d}')
    canvas.restoreState()


def cover(canvas,doc):
    canvas.saveState();canvas.setFillColor(INK);canvas.rect(0,0,W,H,fill=1,stroke=0)
    # Preserve the original illustration; fit its full aspect above the title band.
    width=W;height=width*1.5;canvas.drawImage(str(ASSETS/'box-art.png'),0,H-height,width,height)
    canvas.setFillColor(colors.HexColor('#0A1828'));canvas.rect(0,0,W,77,fill=1,stroke=0)
    canvas.setFillColor(colors.HexColor('#8DE3E7'));canvas.setFont('ManualBold',12)
    canvas.drawCentredString(W/2,58,'FLIGHT MANUAL / FULL CAMPAIGN 1.2')
    canvas.setFillColor(colors.white);canvas.setFont('ManualSans',11)
    canvas.drawCentredString(W/2,39,'A Game Boy Color adventure by Stephan Arrington')
    canvas.setFillColor(colors.HexColor('#C9D4E0'));canvas.setFont('ManualSans',8)
    canvas.drawCentredString(W/2,22,'Documentation revised 2026-10-14 | Original illustrated box art, not an in-game frame.')
    canvas.restoreState()


def render_pdf(pages):
    st=styles();story=[Spacer(1,450),PageBreak()]
    for page_index,(title,blocks) in enumerate(pages):
        story.append(Paragraph(escape(title),st['title']))
        for block in blocks:
            kind=block[0]
            if kind in ('p','h'):story.append(Paragraph(block[1],st[kind]))
            elif kind=='box':
                tab=Table([[Paragraph(block[1],st['box'])]],colWidths=[W-68])
                tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#E9F3EF')),
                    ('BOX',(0,0),(-1,-1),.5,colors.HexColor('#A7CECA')),
                    ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
                    ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
                story.extend([tab,Spacer(1,8)])
            elif kind=='table':
                _,headers,rows,widths=block;scale=(W-68)/sum(widths)
                cells=[[Paragraph(escape(str(v)),st['tablehead' if r==0 else 'table']) for v in row]
                    for r,row in enumerate([headers]+rows)]
                tab=Table(cells,colWidths=[v*scale for v in widths],repeatRows=1,hAlign='LEFT')
                tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),TEAL),('VALIGN',(0,0),(-1,-1),'TOP'),
                    ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#EDF2F1'),colors.HexColor('#F7F8F4')]),
                    ('LINEBELOW',(0,0),(-1,0),.5,TEAL),('LEFTPADDING',(0,0),(-1,-1),6),
                    ('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),
                    ('BOTTOMPADDING',(0,0),(-1,-1),5)]))
                story.extend([tab,Spacer(1,9)])
            elif kind=='image':
                _,name,width,caption=block;im=Image.open(ASSETS/name);height=width*im.height/im.width
                story.append(KeepTogether([PDFImage(str(ASSETS/name),width=width,height=height),Paragraph(escape(caption),st['caption'])]))
            elif kind=='images':
                cells=[]
                for name,caption in block[1]:
                    cells.append([PDFImage(str(ASSETS/name),width=160,height=144),Spacer(1,5),Paragraph(escape(caption),st['caption'])])
                tab=Table([cells],colWidths=[(W-68)/len(cells)]*len(cells))
                tab.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10)]))
                story.append(KeepTogether([tab,Spacer(1,6)]))
        if page_index != len(pages)-1:story.append(PageBreak())
    output=OUTPUT/'Starfall-Salvage-Full-Campaign-Manual.pdf'
    doc=SimpleDocTemplate(str(output),pagesize=letter,rightMargin=34,leftMargin=34,
        topMargin=49,bottomMargin=44,title='Starfall Salvage 1.2 - Full Campaign Flight Manual',
        author='Stephan Arrington',subject='Instructions for the eighteen-mission Game Boy Color campaign and Arcade')
    doc.build(story,onFirstPage=cover,onLaterPages=page_background)
    return output


def render_text(pages):
    md=['# Starfall Salvage 1.2 - Full Campaign Flight Manual','',
        'Game version 1.2. Documentation revised 2026-10-14.','',
        'A Game Boy Color adventure by Stephan Arrington.','',
        'Cover: original illustrated box art, not a gameplay frame.','']
    ht=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Starfall Salvage - Full Campaign Flight Manual</title>',
        '<style>body{font:16px/1.6 system-ui;color:#152d42;background:#faf9f2;max-width:820px;margin:32px auto;padding:24px}h1,h2{color:#08787d}section{break-after:page;border-top:2px solid #c79135;padding-top:24px;margin-top:32px}table{border-collapse:collapse;width:100%;font-size:14px}th{background:#08787d;color:white}td,th{padding:9px;border-bottom:1px solid #c8d2d3;text-align:left}aside{padding:16px;background:#e9f3ef}img{max-width:100%;image-rendering:pixelated}figcaption{font-size:12px;color:#556779}.cover{image-rendering:auto;max-width:360px}</style>',
        '<h1>Starfall Salvage 1.2</h1><p><b>Full Campaign Flight Manual</b><br>By Stephan Arrington<br>Documentation revised 2026-10-14</p>',
        '<img class="cover" src="assets/box-art.png" alt="Original illustrated box art"><p>Illustrated box art, not a gameplay frame.</p>']
    for title,blocks in pages:
        md.extend(['## '+title,'']);ht.extend(['<section><h2>'+html.escape(title)+'</h2>'])
        for b in blocks:
            kind=b[0]
            if kind in ('p','box','h'):
                text=b[1];markdown=text.replace('<b>','**').replace('</b>','**')
                md.extend([('### ' if kind=='h' else '> ' if kind=='box' else '')+markdown,''])
                tag='h3' if kind=='h' else 'aside' if kind=='box' else 'p';ht.append(f'<{tag}>{text}</{tag}>')
            elif kind=='table':
                _,headers,rows,_=b;md.append('| '+' | '.join(headers)+' |');md.append('| '+' | '.join(['---']*len(headers))+' |')
                md.extend('| '+' | '.join(str(v) for v in row)+' |' for row in rows);md.append('')
                ht.append('<table><thead><tr>'+''.join('<th>'+html.escape(v)+'</th>' for v in headers)+'</tr></thead><tbody>')
                ht.extend('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows);ht.append('</tbody></table>')
            elif kind=='image':
                _,name,_,caption=b;md.extend([f'![{caption}](assets/{name})','',caption,''])
                ht.append(f'<figure><img width="320" src="assets/{name}" alt="{html.escape(caption)}"><figcaption>{html.escape(caption)}</figcaption></figure>')
            elif kind=='images':
                ht.append('<div style="display:flex;gap:24px;flex-wrap:wrap">')
                for name,caption in b[1]:
                    md.extend([f'![{caption}](assets/{name})','',caption,''])
                    ht.append(f'<figure style="flex:1;min-width:200px;margin:0"><img width="320" src="assets/{name}" alt="{html.escape(caption)}"><figcaption>{html.escape(caption)}</figcaption></figure>')
                ht.append('</div>')
        ht.append('</section>')
    ht.append('</html>');(STAGE/'INSTRUCTIONS.md').write_text('\n'.join(md)+'\n')
    (STAGE/'INSTRUCTIONS.html').write_text('\n'.join(ht)+'\n')


def main():
    pending=(NATIVE_ROM_SHA256,NATIVE_QUALIFICATION,BROWSER_QUALIFICATION)
    if any(value.startswith('TODO') for value in pending):
        raise SystemExit('Final 1.2 ROM identity and qualification summaries are required before generating player documents.')
    if len(NATIVE_ROM_SHA256)!=64 or any(c not in '0123456789abcdef' for c in NATIVE_ROM_SHA256):
        raise SystemExit('NATIVE_ROM_SHA256 must be the final qualified native ROM SHA-256.')
    OUTPUT.mkdir(parents=True,exist_ok=True);ASSETS.mkdir(parents=True,exist_ok=True)
    for name in ('plugins/starfall/engine/src/starfall_encounter.c','plugins/starfall/engine/src/starfall_objectives.c',
        'plugins/starfall/engine/src/starfall_save.c','plugins/starfall/engine/include/starfall_save.h',
        'plugins/starfall/engine/src/starfall_ui.c','plugins/starfall/engine/src/starfall_screens.c',
        'plugins/starfall/engine/src/starfall_audio.c','CREDITS.md',
        'docs/NATIVE-VERIFICATION.json','docs/BROWSER-VERIFICATION.json','docs/HARDWARE-REPORT-v1.2.json'):
        INPUTS[name]=digest(ROOT/name)
    pages=content();render_text(pages);output=render_pdf(pages)
    (ASSETS/'source-provenance.json').write_text(json.dumps(INPUTS,indent=2)+'\n')
    receipts={'status':'Version 1.2 public instructions include owner-confirmed Chromatic play; visual review pending.',
        'game_version':VERSION,'documentation_revision':DOCS_REVISION,'installation_revision':'public-release-and-owner-confirmed-chromatic','screenshot_rom_sha256':NATIVE_ROM_SHA256,
        'author':'Stephan Arrington','coverage':{'story_missions':18,'story_rooms':72,'zones':6,'arcade_classic_rooms':12},
        'inputs_sha256':INPUTS,'generator_sha256':digest(Path(__file__)),'pdf_sha256':digest(output),
        'screenshot_captions_explicit':True,'embedded_gameplay_screenshots':9,'old_release_files_untouched':True,'native_build_or_device_operation':False,
        'outputs':{'pdf':str(output.relative_to(STAGE)),'markdown':'INSTRUCTIONS.md','html':'INSTRUCTIONS.html'},
        'visual_review':'Pending page rendering and inspection.'}
    (STAGE/'MANUAL-RECEIPTS.json').write_text(json.dumps(receipts,indent=2)+'\n')
    print(output)


if __name__=='__main__':main()
