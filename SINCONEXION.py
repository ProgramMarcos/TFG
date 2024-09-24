# ORDEN DE LAS CLASES:
'''

clases que se pueden detectar según dataset.yaml
 ["libreta", "mano", "volante", "m2", "marca"]

la forma de comprobar qué objeto se está capturando es accediendo mediante
 "resultados[0].boxes.cls"
,que devuelve 0(libreta),1 o 2 (manos), 3 (volante), 4 (marca2) y 5 (marca1)


------------> con el siguiente comando obtenemos

            resultados[0].boxes.(una de las siguientes opciones).item()


xywh: tensor([[x_center, y_center, width, height], ..., device='cuda:0')
Este tensor contiene las coordenadas de las cajas delimitadoras en formato [x_center, y_center, width, height],
donde x_center y y_center son las coordenadas del centro de la caja,
y width y height son el ancho y alto de la caja respectivamente.


xywhn: tensor([[x_center_norm, y_center_norm, width_norm, height_norm], ...], device='cuda:0')
Similar a xywh, pero los valores están normalizados respecto al tamaño de la imagen.
Es decir, los valores están en el rango [0, 1] y representan una fracción del ancho o alto de la imagen.

xyxy: tensor([[x_min, y_min, x_max, y_max], ...], device='cuda:0')
Este tensor contiene las coordenadas de las cajas delimitadoras en formato [x_min, y_min, x_max, y_max],
donde (x_min, y_min) es la esquina superior izquierda de la caja y
(x_max, y_max) es la esquina inferior derecha.


xyxyn: tensor([[x_min_norm, y_min_norm, x_max_norm, y_max_norm], ...], device='cuda:0')
Similar a xyxy, pero los valores están normalizados respecto al tamaño de la imagen.
Es decir, los valores están en el rango [0, 1] y representan una fracción del ancho o alto de la imagen.



'''
########################  INICIO DE PROGRAMA  ###############################

# importamos librerías
import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from collections import defaultdict
import math
import pyads
from ctypes import sizeof



# Leer nuestro modelo
model = YOLO("best.pt")

# Realizar VideoCaptura
cap = cv2.VideoCapture(0)

# declaro variables que necesito
n = 0
track_history = defaultdict(lambda: [])  # método que permite crear una
# estructura de datos que actúa como un diccionario estándar,
# pero con la diferencia de que cuando intentas acceder a una clave
# que no existe, en lugar de lanzar un error, crea automáticamente un
# valor predeterminado para esa clave.
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

# detección de objetos---> variables
hayLibro = False
hayMano = False
hayVolante = False
marca1 = False
marca2 = False
prim = 0
primera = 0
cStop = 0

# Lectura de variables de TwinCAT
game_over = False

# variables necesarias para la detección de giros
gIzq = False
gDer = False
centrado = True
alpha = 0
angulo = math.degrees(alpha)
Avance = False
Frena = False

girando = 0
girandoAnt = 0
x1 = 0
x2 = 0
x3 = 0
x4 = 0
y1 = 0
y2 = 0
y3 = 0
y4 = 0
p = 0
cnt = 0
Dini = 0
Dact = 0
Aini = 0
Aact = 0
areaIni = 0
areaAct = 0
clase = None
listclass = []

posVolante = 0

# variables control manos
Izq = False
Der = False

bStop = False
bBorrado = False

izquierda = False
derecha = False

listamano = []


######################   FUNCIÓN DETECCIÓN MANOS Y ACTIVACIÓN DE INTERMITENTES   ########################

def funcionMano(resultados):
    Izq = False
    Der = False
    if len(resultados[0].boxes.xywh) != 0:
        for box in resultados[0].boxes.xywh:
            x_central = box[
                0].item()  # calculo la x_central (es lo más fácil) y comparo con el centro de la imagen para saber si es izq o der
            if x_central < 320:
                Der = True
            elif x_central > 320:
                Izq = True
    return Izq, Der


##############################   INICIO DE PROGRAMA   ###################################
# antes de empezaar comprobamos la conexión




print("Empezando videocaptura")

# empezamos con la videocaptura
while True:




    ret, frame = cap.read()  # leemos la videocaptura
    imag = frame  # guardamos una copia de frame

    if not ret :
        if not ret:
            print("La captura está fallando")
        break
    # Leemos resultados y los vamos guardando
    resultados = model.predict(frame, imgsz=640,
                               conf=0.5)  # anotamos resultados con la confidencia adecuada para la detección

    vari = model(frame, conf=0.5, verbose=False)

    annotator = Annotator(imag, line_width=2)

    results = model.track(imag, persist=True)

    # vemos qué objetos se están detectando
    clases = resultados[0].boxes.cls
    i = 0
    detectedCLS = []
    for i in range(len(clases)):
        cls = int(clases[i].item())
        detectedCLS.append(int(clases[i].item()))

    ################################ REINICIO DE VARIABLES
    if 2 not in detectedCLS:  # reinicio volante
        gIzq = gDer = centrado = Avance = Frena = False
        prim = 0

    if 0 not in detectedCLS:  # reinicio libro
        gIzq = gDer = centrado = Avance = Frena = False
        primera = 0
        girando = 0
        girandoAnt = 0

    if 1 not in detectedCLS:  # reinicio manos
        gIzq = gDer = centrado = Avance = Frena = False
        cStop = 0
        bBorrado = bStop = False

    i = 0
    listaClases = []
    for i in range(len(clases)):
        cls = int(clases[i].item())
        listaClases.append(int(clases[i].item()))
        # print("listaClases: ",listaClases)

        #################      LIBRO    #########################
        if cls == 0 and cls != 2:
            hayLibro = True
            libro = i  # saco la posición en la que está libro dentro de las clases detectadas (por si me hace falta)
            print('libro')
            for l in range(len(clases)):
                if resultados[0].boxes.cls[l] == 0:
                    x_min = resultados[0].boxes.xyxy[l][0].item()
                    y_min = resultados[0].boxes.xyxy[l][1].item()
                    x_max = resultados[0].boxes.xyxy[l][2].item()
                    y_max = resultados[0].boxes.xyxy[l][3].item()
                    x_cent = resultados[0].boxes.xywh[l][0].item()
                    y_cent = resultados[0].boxes.xywh[l][1].item()
                    width = resultados[0].boxes.xywh[l][2].item()
                    height = resultados[0].boxes.xywh[l][3].item()

                    x_00 = x_min
                    y_00 = y_min
                    x_0n = x_min + width
                    y_0n = y_max - height
                    x_n0 = x_max - width
                    y_n0 = y_min - height
                    x_nn = x_max
                    y_nn = y_max

            if results[0].boxes.id is not None and results[0].masks is not None:
                masks = results[0].masks.xy
                track_ids = results[0].boxes.id.int().cpu().tolist()
                for mask, track_id in zip(masks, track_ids):
                    annotator.seg_bbox(mask=mask, mask_color=colors(track_id, True), track_label=str(track_id))
                    # obtengo los primeros y ultimos puntos de la primera y última fila de la máscara
                    # que en si son las esquinas que delimitan el objeto
                    if len(mask) > 0:
                        for point in mask:
                            x, y = point
                            # print("point: ",x,y)
                            # print("x00: ",x_00)
                            if x_00 < x < x_00 + 5:
                                x1 = x
                                y1 = y
                            elif x_nn - 5 < x < x_nn:
                                x2 = x
                                y2 = y
                            elif y_00 < y < y_00 + 5:
                                y3 = y
                                x3 = x
                            elif y_nn - 5 < y < y_nn:
                                y4 = y
                                x4 = x

                        dx_d = x3 - x1
                        dy_d = y3 - y1
                        dx_i = x2 - x3
                        dy_i = y2 - y3
                        modulo3_1 = math.sqrt((x3 - x1) ** 2 + (y3 - y1) ** 2)
                        modulo3_2 = math.sqrt((x3 - x2) ** 2 + (y3 - y2) ** 2)

                        '''print("p1=", x1, y1)
                        print("p2=", x2, y2)
                        print("p3=", x3, y3)
                        print("p4=", x4, y4)
                        print("p00: ", x_00,y_00)
                        print("pnn: ",x_nn,y_nn)'''

                        # Ordeno la máscara por coordenada
                        sorted_mask = mask[mask[:, 1].argsort()]

                        # primera fila
                        # first point first row
                        fpfr = sorted_mask[0]
                        # last point first row
                        lpfr = sorted_mask[sorted_mask[:, 1].argmax()]

                        # última fila
                        # first point last row
                        fplr = sorted_mask[sorted_mask[:, 1].argmax()]
                        # last point last row
                        lplr = sorted_mask[-1]

                        # extraigo coordenadas x e y de cada punto
                        xff, yff = fpfr
                        xlf, ylf = lpfr
                        xfl, yfl = fplr
                        xll, yll = lplr

                        if primera == 0:  # si es la primera vez
                            centrado = True
                            gDer = False
                            gIzq = False

                            Aini = width * height
                            Aact = Aini
                            primera += 1  # ya no es más la primera vez

                        elif primera > 0:
                            Aact = width * height

                            if Aact > Aini * 2:
                                Avance = True
                                Frena = False
                            elif Aact < Aini:
                                Avance = False
                                Frena = True
                            else:
                                Avance = False
                                Frena = False

                        centrado = False
                        if (xff <= x_00 + 15 and yff <= y_00 + 15):
                            centrado = True
                            gDer = False
                            gIzq = False
                            alpha = 0
                            if width < height:
                                girando = girandoAnt
                            else:
                                girando = 0

                        if centrado and width < height:
                            centrado = False
                            alpha = math.pi / 2
                        if not centrado:
                            if modulo3_1 < modulo3_2:
                                if (girando == 0 or girando == 1) and abs(alpha) != math.pi / 2:
                                    gDer = False
                                    gIzq = True  # angulo positivo
                                    girando = 1
                                    alpha = math.atan2(dy_i, dx_i)
                                elif girandoAnt == -1:
                                    gIzq = False
                                    gDer = True
                                    girando = -1
                                    dx = x1 - x4
                                    dy = y1 - y4
                                    alpha = math.atan2(dy, dx)
                                elif (girando == 0 or girando == 1) and abs(alpha) == math.pi / 2:
                                    gIzq = True
                                    gDer = False
                                    girando = 1
                                    alpha = math.pi / 2
                                girandoAnt = girando

                            elif modulo3_2 < modulo3_1:
                                if (girando == 0 or girando == -1) and abs(alpha) != math.pi / 2:
                                    gIzq = False
                                    gDer = True  # angulo negativo
                                    girando = -1
                                    alpha = math.atan2(dy_d, dx_d)
                                elif girandoAnt == 1:
                                    gDer = False
                                    gIzq = True
                                    girando = 1
                                    dx = x4 - x2
                                    dy = y4 - y2
                                    alpha = math.atan2(dy, dx)
                                elif (girando == 0 or girando == -1) and abs(alpha) == math.pi / 2:
                                    gIzq = False
                                    gDer = True  # angulo negativo
                                    girando = -1
                                    alpha = (-1) * math.pi / 2
                                girandoAnt = girando

                        print('Izquierda : ', gIzq, ' ; Derecha : ', gDer, ' ; centrado : ', centrado)
                        print("Avance: ", Avance, "Freno: ", Frena)
                        angulo = math.degrees(alpha)
                        print("angulo: ", angulo)

        #################      MANOS   #########################
        elif cls == 1:
            hayMano = True
            izquierda, derecha = funcionMano(resultados)

            if (izquierda or derecha) and not (izquierda and derecha):
                cStop += 1
                bStop = False
                if cStop == 10:
                    cStop = 0
                    bStop = True
                    print("Paro Operativo activado -----> Pasando a Modo Stop")

            if izquierda and derecha:
                cStop = 0
                bBorrado = True

                print(" Modo Borrado activado")
            # print('izquierda: ', izquierda)  # izq ->
            # print('derecha: ', derecha)  # derecha <-


        #################      VOLANTE    #########################
        elif cls == 2 and cls != 0:
            hayVolante = True
            # print(len(clases))
            # listaManos = funcionMano(resultados, hayVolante)
            print("hay volante")

            if prim == 0:
                for w in range(len(clases)):
                    if resultados[0].boxes.cls[w] == 2:  # recorro los objetos detectados para buscar el volante
                        ancho = resultados[0].boxes.xywh[w][2].item()  # saco width
                        alto = resultados[0].boxes.xywh[w][3].item()  # saco height
                        areaIni = ancho * alto
                        prim = 1
            else:
                for w in range(len(clases)):
                    if resultados[0].boxes.cls[w] == 2:  # recorro los objetos detectados para buscar el volante
                        ancho = resultados[0].boxes.xywh[w][2].item()  # saco width
                        alto = resultados[0].boxes.xywh[w][3].item()  # saco height
                        areaAct = ancho * alto
                if areaAct > areaIni * 1.02:
                    Avance = True
                    Frena = False
                    # print("avance:",Avance )

                elif areaAct < areaIni / 1.02:
                    Avance = False
                    Frena = True
                    # print("frena: ",Frena)
                else:
                    Avance = False
                    Frena = False
                # print(resultados[0].boxes.cls)
                for j in range(len(clases)):
                    if resultados[0].boxes.cls[j] == 4:  # detecto marca
                        marca1 = True
                        primeraMarca = j

                    elif resultados[0].boxes.cls[j] == 3:  # detecto m2
                        marca2 = True
                        segundaMarca = j

                if marca1 and marca2:
                    y_m1 = resultados[0].boxes.xywh[primeraMarca][1].item()
                    x_m1 = resultados[0].boxes.xywh[primeraMarca][0].item()
                    y_m2 = resultados[0].boxes.xywh[segundaMarca][1].item()
                    x_m2 = resultados[0].boxes.xywh[segundaMarca][0].item()

                    # print("marca1: ",x_m1,y_m1)
                    # print("marca2: ",x_m2,y_m2) # la marca 2 'siempre' tiene menor x

                    dx = x_m1 - x_m2
                    dy = y_m1 - y_m2
                    alpha = math.atan2(dy, dx)
                    if y_m2 <= y_m1 - 15:
                        # print("giro izquierda")
                        centrado = False
                        gDer = False
                        gIzq = True
                        alpha = math.atan2(dy, dx)


                    elif y_m1 <= y_m2 - 15:
                        # print("giro derecha")
                        centrado = False
                        gDer = True
                        gIzq = False
                        alpha = math.atan2(dy, dx)
                    else:
                        # print("centrado")
                        centrado = True
                        gDer = False
                        gIzq = False
                        alpha = 0

                    print('Izquierda : ', gIzq, ' ; Derecha : ', gDer, ' ; centrado : ', centrado)
                    print("Avance: ", Avance, "Freno: ", Frena)
                    angulo = math.degrees(alpha)
                    print("angulo: ", angulo)

                marca1 = False
                marca2 = False



        else:
            hayLibro = False
            hayMano = False
            hayVolante = False

    # Dibujar consignas en la imagen
    consigna_text = ""
    consignas_text = []
    if Avance:
        consigna_text = "Avanzar"
        consignas_text.append(consigna_text)
    if Frena:
        consigna_text = "Frenar"
        consignas_text.append(consigna_text)
    if gIzq:
        consigna_text = "Girar a la izquierda"
        consignas_text.append(consigna_text)
    if gDer:
        consigna_text = "Girar a la derecha"
        consignas_text.append(consigna_text)
    if game_over:
        consigna_text = "GAME OVER"
        consignas_text.append(consigna_text)
    if bStop:
        consignas_text = []
        consigna_text = "PASANDO A STOP OPERATIVO"
        consignas_text.append(consigna_text)
    if bBorrado:
        consignas_text = []
        consigna_text = "PASANDO A MODO BORRADO"
        consignas_text.append(consigna_text)
    # print(consignas_text)

    for Ctxt in range(len(consignas_text)):
        cv2.putText(imag, consignas_text[Ctxt], (50, (1 + Ctxt) * 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                    cv2.LINE_AA)
    imag = annotator.result()
    # cv2.imshow("Salida", imag)

    # muestro el video con la captura que estoy realizando
    cv2.imshow("instance-segmentation-object-tracking", resultados[0].plot())

    # Cerrar nuestro programa al pulsar esc (codico ASCII de esc=27)
    if cv2.waitKey(1) == 27:
        break

# finalizo captura y cierro ventanas
cap.release()
cv2.destroyAllWindows()



