Внимание!

Используется пропатченая версия библиотеки "framework-arduino-samd-seed"

https://forum.seeedstudio.com/t/require-3-hardware-uarts/255453/8
http://kio-denshi.com/hp/index.php?Technical%20Information%2Fetc.%2FXIAO%20Serial%20Extension%202

добавлены две папки [Serial2, Serial3] по пути ~/.platformio/packages/framework-arduino-samd-seeed/libraries
с содержимым:
Serial2.h
```
#ifndef Serial2_h
#define Serial2_h

#include "variant.h"

void SERCOM2_Handler(void);

#endif
```

Serial2.cpp
#include "Serial2.h"

Uart Serial2( &sercom2, PIN_SERIAL2_RX, PIN_SERIAL2_TX, PAD_SERIAL2_RX, PAD_SERIAL2_TX ) ;

void SERCOM2_Handler()
{
  Serial2.IrqHandler();
}
```

Serial3.h
```
#ifndef Serial3_h
#define Serial3_h

#include "variant.h"

void SERCOM0_Handler(void);

#endif
```

Serial3.cpp
```
#include "Serial3.h"

Uart Serial3( &sercom0, PIN_SERIAL3_RX, PIN_SERIAL3_TX, PAD_SERIAL3_RX, PAD_SERIAL3_TX ) ;

void SERCOM0_Handler()
{
  Serial3.IrqHandler();
}
```

доавлены строки 

```
// Serial2
extern Uart Serial2;
#define PIN_SERIAL2_TX       (4ul)
#define PIN_SERIAL2_RX       (5ul)
#define PAD_SERIAL2_TX       (UART_TX_PAD_0)
#define PAD_SERIAL2_RX       (SERCOM_RX_PAD_1)
// Serial3
extern Uart Serial3;
#define PIN_SERIAL3_TX       (10ul)
#define PIN_SERIAL3_RX       (9ul)
#define PAD_SERIAL3_TX       (UART_TX_PAD_2)
#define PAD_SERIAL3_RX       (SERCOM_RX_PAD_1)

```
в файл ~/.platformio/packages/framework-arduino-samd-seeed/variants/XIAO_m0/variant.h возле раздела // Serial1


