----------------------------MIM-1----------------------------------

esto es un proyecto que empece usando catgpt y escrito en Python. Decir que yo no soy programador ni entiendo de programacion, pero tube una idea y quise hacerla realidad. 


lLa idea es crear un sampler multiplataforma y pense orimeramente en BSD linux, ¿ y por que ?... pues por que un equipo para este sistema operativo es mucho mas economico para el preyecto. la idea final es montar tu propio DAW personalizado y totalmente portatil, y me refiero a que si quieres un DAW asi pues puedes pensr  `` eso ya existe, coges un controlador midi, un ordenador, le metes el softwere y a sonar.´´  pero esto va mas aya, por que es un todo en uno.

Esto es lo siguiente: 

- coges un mini PC adecuado

    - metes este sampler que es capaz de cargar el soundfont que tu elijas 
    - asignarlo a uno de sus 16 canales 
    - modificar ese sonido a tu antojo, guardarlo, usar hasta 16 capas de sonido personalizado
    - egun el aparato que elijas:
          - posibilidad de almacenamiento , ( 4, 8, 12 Tb, internos,)
          - posibilidad de memoria la que te admita.
          - posibilidad de mas almacenamiento externo, ( USB, SSD, Mv2, etc... )
          - Posibilidad de ponerle un monitor de ( 13, 15, 17 pulgadas, etc...)
          - posibilidad de que el monitor sea tactil, son alimentados por el puerto tuntherbol por lo que no necesitan alimentacion externa.
          - posibilidad de un monton de puertos de conexion, todas las que tenga el aparato elegido
          - posibilidad de un monitor externo

En definitiva todas las posibilidades que te imagines y siempre sera personalizado.

tambien podrias usar un ipad, una tablet android, un moniPC con windows o un MacMini, todo depende de como lo quieras y puedas personalizar.


y dicho esto imagino que  ya sabras que la idea es meter esto dentro de un controlador midi, adaptandolo y haciendo un solo bloque que sera totalmente portable, lo enciendes y listo


como ni soy programador ni entiendo de programacion ni nada, solo llegue hasta aqui por que chatgpt aun tiene mucho que aprender y llego un punto en el que solo daba errores.

falta mucho por hacer aun: 
      - ajustar la interface para que sea fluida y no tenga comportamientos anumalos
      - tiene que usar codigo libre para poder implantar fluidsynth para manejar lo soundfont
      - tiene que poder ser multi capa, hasta los 16 canales
      - tiene que poder samplear correctamente los archivos wav y mp3
      - tiene que incluir el codigo de sfzero para los .fsz
      - falta que sea funcional la salida de vumetros
      - falta que se funcional los osciladores, un sampler delay, el modulo efectos, que cargue y sea funcional el modulo VST
      - falta un secuenciador midi en pantalla que lea y grave hasta 16 pistas
      - falta el modulo plAY
      - falta el ajustas del audio, ( selector de fuentes, midi, etc...)

en definitiva es un proyecto que me gustaria haberlo podido terminar para que todo el mundo pudiese usarlo por que quiero que sea de codigo libre