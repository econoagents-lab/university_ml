# Decision Playbook · Riesgo de Caída

## 1. Objetivo

Convertir un score de riesgo en una acción comercial concreta.

---

## 2. Tabla de decisión

| Score | Nivel | Acción | Responsable | SLA | Resultado esperado |
|---:|---|---|---|---|---|
| 0.00 - 0.39 | Bajo | Seguimiento estándar | Asesor | Semana | Mantener control |
| 0.40 - 0.69 | Medio | Contacto priorizado | Asesor | 24 horas | Identificar bloqueo |
| 0.70 - 1.00 | Alto | Escalamiento comercial | Jefe comercial | Hoy | Salvar operación o anticipar caída |

---

## 3. Acciones sugeridas por causa probable

### Sin cuota inicial

- Confirmar fecha de pago.
- Validar impedimento financiero.
- Registrar compromiso.

### Muchos días en tubería

- Revisar motivo de demora.
- Escalar documentación pendiente.
- Reconfirmar intención de compra.

### Precio alto o descuento bajo

- Evaluar sensibilidad del cliente.
- Revisar alternativas de unidad.
- Simular escenario financiero.

### Cambio de unidad

- Detectar insatisfacción de producto.
- Comparar alternativas.
- Evitar que el cambio oculte pérdida de intención.

---

## 4. Registro de feedback

Después de la acción:

```text
accion_tomada
fecha_accion
responsable
resultado_cliente
siguiente_paso
resultado_30d
```

---

## 5. Regla de oro

No basta con decir “riesgo alto”. La salida final debe ser:

```text
riesgo + causa probable + acción + responsable + fecha + medición
```
