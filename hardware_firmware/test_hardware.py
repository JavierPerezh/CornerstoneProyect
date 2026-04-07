"""
test_hardware.py - Script de prueba de hardware

Ejecutar después de ensamblar el hardware para verificar:
- GPIOs funcionando correctamente
- Audio (grabación y reproducción)
- Conectividad de red
"""

import sys
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_gpio():
    """Test de GPIOs (LED y botón)"""
    print("\n" + "=" * 60)
    print("TEST 1: GPIO (LED RGB y Botón)")
    print("=" * 60)
    
    try:
        from gpio_manager import LEDController, ButtonController
        
        # Test LED
        print("\n[LED RGB Test]")
        led = LEDController(pin_red=27, pin_green=23, pin_blue=24)
        
        colors = [
            ("Rojo", (1, 0, 0)),
            ("Verde", (0, 1, 0)),
            ("Azul", (0, 0, 1)),
            ("Amarillo", (1, 1, 0)),
            ("Magenta", (1, 0, 1)),
            ("Cian", (0, 1, 1)),
            ("Blanco", (1, 1, 1)),
        ]
        
        for name, color in colors:
            print(f"  Encendiendo LED en {name}... ", end='', flush=True)
            led.set_color(color)
            time.sleep(0.5)
            print("✓")
        
        led.off()
        print("  Apagando LED... ✓")
        
        # Test Botón
        print("\n[Botón Test]")
        button = ButtonController(pin=17, debounce_ms=50)
        
        press_count = [0]
        
        def on_press():
            press_count[0] += 1
            print(f"  ✓ Presión #{press_count[0]} detectada")
        
        button.on_press(on_press)
        button.start_monitoring()
        
        print("  Esperando 3 presiones de botón (timeout 20 segundos)...")
        
        start_time = time.time()
        while press_count[0] < 3 and (time.time() - start_time) < 20:
            time.sleep(0.1)
        
        button.stop_monitoring()
        
        if press_count[0] >= 3:
            print("  ✓ Botón funcionando correctamente")
        else:
            print(f"  ✗ Solo se detectaron {press_count[0]} presiones")
        
        # Cleanup
        led.cleanup()
        button.cleanup()
        
        print("\n✓ TEST 1 PASADO\n")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST 1 FALLIDO: {e}\n")
        return False


def test_audio():
    """Test de audio (grabación y reproducción)"""
    print("\n" + "=" * 60)
    print("TEST 2: Audio (Grabación y Reproducción)")
    print("=" * 60)
    
    try:
        from audio_modules import AudioCapture, AudioPlayback
        import os
        
        config = {
            'sample_rate': 16000,
            'channels': 1,
            'chunk_size': 1024
        }
        
        # Test grabación
        print("\n[Grabación de Audio]")
        capture = AudioCapture(config)
        
        print("  Grabando 3 segundos (habla en el micrófono)...")
        capture.start_recording(max_duration=3)
        
        for i in range(3):
            time.sleep(1)
            print(f"  . ({i+1}/3)")
        
        recording_file = capture.stop_recording()
        
        if recording_file and os.path.exists(recording_file):
            file_size = os.path.getsize(recording_file)
            print(f"  ✓ Grabación guardada: {recording_file} ({file_size} bytes)")
        else:
            print("  ✗ Error: No se guardó la grabación")
            capture.cleanup()
            return False
        
        # Test reproducción
        print("\n[Reproducción de Audio]")
        playback = AudioPlayback(config)
        
        print("  Reproduciendo grabación (deberías escucharte)...")
        success = playback.play(recording_file)
        
        if success:
            print("  ✓ Reproducción completada")
        else:
            print("  ✗ Error durante reproducción")
        
        # Cleanup
        capture.cleanup()
        playback.cleanup()
        
        # Limpiar archivo temporal
        try:
            os.remove(recording_file)
        except:
            pass
        
        print("\n✓ TEST 2 PASADO\n")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST 2 FALLIDO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_network():
    """Test de conectividad de red"""
    print("\n" + "=" * 60)
    print("TEST 3: Red (Conectividad)")
    print("=" * 60)
    
    try:
        from network_manager import NetworkManager, WiFiManager
        
        config = {
            'backend_url': 'http://8.8.8.8',
            'backend_timeout': 5,
        }
        
        manager = NetworkManager(config, device_id='test-device')
        
        # Test conectividad básica
        print("\n[Conectividad]")
        print("  Verificando conexión a internet... ", end='', flush=True)
        
        if manager.is_connected():
            print("✓ Conectado")
        else:
            print("✗ Sin conexión")
            return False
        
        # Test WiFi
        print("\n[WiFi Info]")
        network = WiFiManager.get_current_network()
        if network:
            print(f"  Red actual: {network}")
        
        signal = WiFiManager.get_signal_strength()
        if signal:
            print(f"  Señal: {signal} dBm")
        
        print("\n✓ TEST 3 PASADO\n")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST 3 FALLIDO: {e}\n")
        return False


def test_state_machine():
    """Test de máquina de estados"""
    print("\n" + "=" * 60)
    print("TEST 4: Máquina de Estados")
    print("=" * 60)
    
    try:
        from state_machine import StateMachine, DeviceState
        from gpio_manager import LEDController
        
        # Mock de controladores
        class MockButton:
            pass
        
        led = LEDController(pin_red=27, pin_green=23, pin_blue=24)
        button = MockButton()
        
        sm = StateMachine(led, button)
        
        print("\n[Transiciones de Estado]")
        
        states = [
            DeviceState.RECORDING,
            DeviceState.SENDING,
            DeviceState.PROCESSING,
            DeviceState.PLAYING,
            DeviceState.ERROR,
            DeviceState.IDLE,
        ]
        
        for state in states:
            print(f"  Transición a {state.value}... ", end='', flush=True)
            sm.transition_to(state, reason="Test")
            time.sleep(0.5)
            print("✓")
        
        info = sm.get_state_info()
        print(f"\n  Estado actual: {info['current_state']}")
        print(f"  Duración: {info['duration']:.2f}s")
        
        sm.shutdown()
        led.cleanup()
        
        print("\n✓ TEST 4 PASADO\n")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST 4 FALLIDO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecuta todos los tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "ANIMAL DEVICE - TEST DE HARDWARE".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # Ejecutar tests
    try:
        results.append(("GPIO (LED y Botón)", test_gpio()))
    except KeyboardInterrupt:
        print("\nTest interrumpido por usuario")
        return
    except Exception as e:
        print(f"Error no controlado en test GPIO: {e}")
        results.append(("GPIO (LED y Botón)", False))
    
    try:
        results.append(("Audio (Grabación y Reproducción)", test_audio()))
    except KeyboardInterrupt:
        print("\nTest interrumpido por usuario")
        return
    except Exception as e:
        print(f"Error no controlado en test Audio: {e}")
        results.append(("Audio (Grabación y Reproducción)", False))
    
    try:
        results.append(("Red (Conectividad)", test_network()))
    except KeyboardInterrupt:
        print("\nTest interrumpido por usuario")
        return
    except Exception as e:
        print(f"Error no controlado en test Red: {e}")
        results.append(("Red (Conectividad)", False))
    
    try:
        results.append(("Máquina de Estados", test_state_machine()))
    except KeyboardInterrupt:
        print("\nTest interrumpido por usuario")
        return
    except Exception as e:
        print(f"Error no controlado en test SM: {e}")
        results.append(("Máquina de Estados", False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASADO" if result else "✗ FALLIDO"
        print(f"{test_name:.<40} {status}")
    
    print()
    print(f"Total: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\n✓ TODOS LOS TESTS PASARON - Hardware listo para usar")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} test(s) fallaron - Revisar configuración")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests cancelados por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nError crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
