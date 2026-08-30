import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import time

# 1. Автопоиск камеры
cap = None
for cam_id in [0, 1, 2]:
    temp_cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
    if temp_cap.isOpened():
        ret, test_frame = temp_cap.read()
        if ret:
            cap = temp_cap
            print(f"[OK] Camera connected: ID {cam_id}")
            break
        temp_cap.release()

if cap is None:
    print("[ERROR] camera doesn't exist!")
    exit()

cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(maxHands=2, detectionCon=0.65)

canvas = None
prev_x, prev_y = 0, 0
smooth_x, smooth_y = 0, 0
SMOOTH_FACTOR = 0.65

# 9 цветов в палитре (BGR)
palette = [
    ("Green", (0, 255, 0)),
    ("Cyan", (255, 255, 0)),
    ("Blue", (255, 0, 0)),
    ("Purple", (255, 0, 128)),
    ("Red", (0, 0, 255)),
    ("Orange", (0, 140, 255)),
    ("Yellow", (0, 255, 255)),
    ("White", (255, 255, 255)),
    ("Black", (15, 15, 15))
]

color_idx = 0
brush_color = palette[color_idx][1]
brush_thickness = 10
eraser_thickness = 55

sizes = [("S", 4), ("M", 10), ("L", 24)]

# Замок для предотвращения бесконечного переключения цвета
pinch_locked = False

clear_btn_timer = 0
CLEAR_HOLD_TIME = 0.8

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    if canvas is None:
        canvas = np.zeros_like(frame)

    hands, frame = detector.findHands(frame, draw=False)

    drawing_active = False
    holding_clear_button = False
    pinch_detected_this_frame = False

    if hands:
        for hand in hands:
            lmList = hand["lmList"]

            raw_tx, raw_ty = lmList[4][0], lmList[4][1]  # Большой палец
            raw_ix, raw_iy = lmList[8][0], lmList[8][1]  # Указательный палец
            raw_mx, raw_my = lmList[12][0], lmList[12][1]  # Средний палец

            # Отрисовка аккуратных хитбоксов на всех кончиках пальцев
            for tip_id in [4, 8, 12, 16, 20]:
                cv2.circle(frame, (lmList[tip_id][0], lmList[tip_id][1]), 7, (255, 255, 255), 1)

            # Проверка жеста «ОК» (щипок: дистанция между большим и указательным)
            dist_pinch = np.hypot(raw_tx - raw_ix, raw_ty - raw_iy)
            is_ok_gesture = (dist_pinch < 38)

            # ПРИОРИТЕТ 1: ЖЕСТ «ОК» (ТОЛЬКО СМЕНА ЦВЕТА, РИСОВАНИЕ ЗАПРЕЩЕНО)
            if is_ok_gesture:
                pinch_detected_this_frame = True
                cx_p, cy_p = (raw_tx + raw_ix) // 2, (raw_ty + raw_iy) // 2

                # Визуальный отклик клика
                cv2.circle(frame, (cx_p, cy_p), 18, (0, 255, 0), cv2.FILLED)
                cv2.circle(frame, (cx_p, cy_p), 22, (255, 255, 255), 2)
                cv2.putText(frame, "COLOR SWITCH", (cx_p - 55, cy_p - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                if not pinch_locked:
                    color_idx = (color_idx + 1) % len(palette)
                    brush_color = palette[color_idx][1]
                    pinch_locked = True
                continue  # ПРЕПЯТСТВУЕТ рисованию этой рукой!

            # ПРИОРИТЕТ 2: ВЗАИМОДЕЙСТВИЕ С КНОПКАМИ S/M/L И CLEAR
            # Кнопки размеров (S, M, L)
            for i, (s_name, s_val) in enumerate(sizes):
                sy1 = 40 + i * 75
                sy2 = sy1 + 60
                if 20 <= raw_ix <= 85 and sy1 <= raw_iy <= sy2:
                    brush_thickness = s_val
                    cv2.rectangle(frame, (18, sy1 - 2), (87, sy2 + 2), (0, 255, 255), 3)

            # Кнопка CLEAR (Очистить холст)
            if 20 <= raw_ix <= 130 and 280 <= raw_iy <= 335:
                holding_clear_button = True
                if clear_btn_timer == 0:
                    clear_btn_timer = time.time()

                elapsed = time.time() - clear_btn_timer
                progress = min(elapsed / CLEAR_HOLD_TIME, 1.0)
                cv2.rectangle(frame, (20, 280), (int(20 + progress * 110), 335), (0, 0, 255), cv2.FILLED)

                if elapsed >= CLEAR_HOLD_TIME:
                    canvas = np.zeros_like(frame)
                    clear_btn_timer = 0

            # ПРИОРИТЕТ 3: РИСОВАНИЕ (1 ПАЛЕЦ) ИЛИ ЛАСТИК (2 ПАЛЬЦА)
            # Точная проверка поднятия пальцев относительно суставов PIP
            index_up = lmList[8][1] < lmList[6][1]
            middle_up = lmList[12][1] < lmList[10][1]

            #Игнорируем область бокового меню при рисовании
            if raw_ix > 140:
                # Фильтр сглаживания
                if smooth_x == 0 and smooth_y == 0:
                    smooth_x, smooth_y = raw_ix, raw_iy
                else:
                    dist_moved = np.hypot(raw_ix - smooth_x, raw_iy - smooth_y)
                    if dist_moved > 3:
                        smooth_x = int(smooth_x * (1 - SMOOTH_FACTOR) + raw_ix * SMOOTH_FACTOR)
                        smooth_y = int(smooth_y * (1 - SMOOTH_FACTOR) + raw_iy * SMOOTH_FACTOR)

                #ЛАСТИК (Подняты указательный + средний)
                if index_up and middle_up:
                    drawing_active = True
                    eraser_x = (smooth_x + raw_mx) // 2
                    eraser_y = (smooth_y + raw_my) // 2

                    cv2.circle(frame, (eraser_x, eraser_y), eraser_thickness // 2, (0, 0, 255), 2)
                    cv2.circle(frame, (eraser_x, eraser_y), 4, (0, 0, 255), cv2.FILLED)
                    cv2.putText(frame, "ERASER", (eraser_x - 30, eraser_y - eraser_thickness // 2 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                    if prev_x != 0 and prev_y != 0:
                        cv2.line(canvas, (prev_x, prev_y), (eraser_x, eraser_y), (0, 0, 0), eraser_thickness)
                    prev_x, prev_y = eraser_x, eraser_y

                #РИСОВАНИЕ (Поднят только указательный)
                elif index_up and not middle_up:
                    drawing_active = True

                    cv2.circle(frame, (smooth_x, smooth_y), brush_thickness + 4, (255, 255, 255), 2)
                    cv2.circle(frame, (smooth_x, smooth_y), brush_thickness, brush_color, cv2.FILLED)
                    cv2.putText(frame, "DRAW", (smooth_x - 20, smooth_y - brush_thickness - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

                    if prev_x == 0 and prev_y == 0:
                        prev_x, prev_y = smooth_x, smooth_y
                    cv2.line(canvas, (prev_x, prev_y), (smooth_x, smooth_y), brush_color, brush_thickness)
                    prev_x, prev_y = smooth_x, smooth_y

    # Разблокировка замка клика, когда пальцы разомкнуты
    if not pinch_detected_this_frame:
        pinch_locked = False

    if not holding_clear_button:
        clear_btn_timer = 0

    if not drawing_active:
        prev_x, prev_y = 0, 0
        smooth_x, smooth_y = 0, 0

    # Смешивание слоев
    img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, img_inv = cv2.threshold(img_gray, 5, 255, cv2.THRESH_BINARY_INV)
    img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
    frame = cv2.bitwise_and(frame, img_inv)
    frame = cv2.bitwise_or(frame, canvas)

    #  РЕНДЕР ИНТЕРФЕЙСА (UI)
    # Кнопки размеров (S / M / L) слева
    for i, (s_name, s_val) in enumerate(sizes):
        sy1 = 40 + i * 75
        sy2 = sy1 + 60
        is_size_sel = (s_val == brush_thickness)
        cv2.rectangle(frame, (20, sy1), (85, sy2), (50, 50, 50), cv2.FILLED)
        cv2.rectangle(frame, (20, sy1), (85, sy2), (0, 255, 255) if is_size_sel else (120, 120, 120),
                      2 if is_size_sel else 1)
        cv2.putText(frame, s_name, (42, sy1 + 42), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Кнопка CLEAR
    cv2.rectangle(frame, (20, 280), (130, 335), (40, 40, 150), 2)
    cv2.putText(frame, "CLEAR", (35, 317), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    # Виджет активного цвета (Справа вверху, без наложений)
    current_name = palette[color_idx][0]
    cv2.putText(frame, current_name, (w - 230, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.circle(frame, (w - 60, 45), 28, (255, 255, 255), 2)
    cv2.circle(frame, (w - 60, 45), 25, brush_color, cv2.FILLED)
    cv2.putText(frame, f"{brush_thickness}px", (w - 75, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    # Подсказка
    cv2.putText(frame, "Pinch OK = Next Color | 1 Finger = Draw | 2 Fingers = Eraser",
                (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    cv2.imshow("Pro Hitbox Virtual Paint", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
