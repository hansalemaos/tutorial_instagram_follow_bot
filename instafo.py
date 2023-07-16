from adbkit import ADBTools
from time import sleep, strftime
import random
import pandas as pd


def get_uiautomator_frame(screenshotfolder="c:\\ttscreenshots"):
    adb.aa_update_screenshot()
    return adb.aa_get_all_displayed_items_from_uiautomator(
        screenshotfolder=screenshotfolder,  # screenshots will be saved here
        max_variation_percent_x=10,
        # used for one of the click functions, to not click exactly in the center - more information below
        max_variation_percent_y=10,  # used for one of the click functions, to not click exactly in the center
        loung_touch_delay=(
            1000,
            1500,
        ),  # with this settings longtouch will take somewhere between 1 and 1,5 seconds
        swipe_variation_startx=10,  # swipe coordinate variations in percent
        swipe_variation_endx=10,
        swipe_variation_starty=10,
        swipe_variation_endy=10,
        sdcard="/storage/emulated/0/",
        # sdcard will be used if you use the sendevent methods, don't pass a symlink - more information below
        tmp_folder_on_sd_card="AUTOMAT",  # this folder will be created in the sdcard folder for using sendevent actions
        bluestacks_divider=32767,
        # coordinates must be recalculated for BlueStacks https://stackoverflow.com/a/73733261/15096247 when using sendevent
    )


ADBTools.aa_kill_all_running_adb_instances()
adb_path = r"C:\ProgramData\chocolatey\bin\adb.exe"
deviceserial = 'localhost:5555'
adb = ADBTools(adb_path=adb_path,
               deviceserial=deviceserial)

adb.aa_start_server()
sleep(3)
adb.aa_connect_to_device()
adb.aa_activate_tesseract(
    tesseractpath=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
usuarios = ['leomessi']
usuario = random.choice(usuarios)
adb.aa_open_website(rf'https://www.instagram.com/{usuario}/')
sleep(random.uniform(3, 4))
adb.aa_input_tap(680, 195)
sleep(random.uniform(4, 5))

while True:
    df = get_uiautomator_frame()
    df['bb_keygroup'] = df.bb_keys_hierarchy.str[:14]
    allgroups = []
    for name, group in df.groupby('bb_keygroup'):
        if len(group) == 4:
            indi = group.index[0]
            group2 = pd.concat([df.iloc[indi + 1:indi + 2],
                                group], ignore_index=True)
            allgroups.append(group2.copy())
    dfa = pd.concat([allgroups[x][3:4] for x in range(len(allgroups))
                     ], ignore_index=True)
    dfa2 = pd.concat([allgroups[x][:1] for x in range(len(allgroups))
                      ], ignore_index=True)

    dft = adb.aa_ocr_df_with_tesseract_multiprocessing(dfa, language='eng', cpus=5)
    dft2 = adb.aa_ocr_df_with_tesseract_multiprocessing(dfa2, language='eng', cpus=5)
    allresults = []
    for r in range(len(allgroups)):
        user = allgroups[r][:1].copy()
        user['aa_username'] = dft.bb_scanned_text.iloc[r]
        user['aa_status'] = dft2.bb_scanned_text.iloc[r]
        allresults.append(user)
    df2 = pd.concat(allresults, ignore_index=True)
    df2 = df2.loc[df2.aa_status == 'Follow']
    if not df2.empty:
        dfchoosen = df2.sample(1)
        dfchoosen.iloc[0].ff_bb_tap_center_variation(10, 10)
        followtime = strftime("%Y_%m_%d_%H_%M_%S")
        with open('c:\\myfollows.txt', mode='a', encoding='utf-8') as f:
            f.write(f'{dfchoosen.aa_username.iloc[0]},{followtime}\n')
    else:
        print('outro usuario')

    sleep(random.uniform(4, 10))
