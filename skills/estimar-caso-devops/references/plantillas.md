# Plantillas de salida

Los comentarios se publican con `wit_work_item_comment_write`, `format: Html`. Pasar el texto con
tildes y simbolos (₡, ñ) tal cual: el conector maneja el encoding.

Mencion (resolver el GUID con `core_get_identity_ids` y el nombre completo; Gerson es
`29c2ec0f-5ed2-6b24-b590-3ce280e34d03`):

```html
<a href="#" data-vss-mention="version:2.0,<GUID>">@Nombre Completo</a>
```

## Contenido
- A. Comentario de negocio (ESTIMAR)
- B. Nota tecnica para desarrollo (ESTIMAR)
- C. Comentario de rechazo o bloqueo
- D. Aviso en otro ticket afectado
- E. Resumen final para el usuario
- Lista de verificacion antes de mostrar un borrador

## A. Comentario de negocio

Para negocio y QA. Explica la **causa encontrada**, no repite el sintoma que ya escribio quien reporto.
Sin archivo:linea. Si el mismo defecto afecta otro flujo no mencionado, se dice aqui (salvo que el
usuario haya pedido documentarlo acotado).

```html
<p><b>Analisis del caso</b></p>
<p>[Causa en lenguaje de negocio: que hace hoy el sistema y por que da el resultado reportado.]</p>
<p>[Si aplica: el mismo ajuste corrige tambien X / el defecto tambien afecta Y.]</p>
<p><b>Estimado:</b> [N] horas ([que incluye, en una linea]).</p>
<p>cc. <a href="#" data-vss-mention="version:2.0,29c2ec0f-5ed2-6b24-b590-3ce280e34d03">@Gerson Barboza Piedra</a></p>
```

Ejemplo (basado en el 2051):

> **Analisis del caso**
> Cuando una factura se paga con transferencia y se da vuelto en efectivo, el sistema resta ese vuelto
> de la transferencia en lugar de restarlo del efectivo de la caja. Por eso el cierre muestra mas
> efectivo del que realmente hay. El mismo calculo se usa en los retiros de caja, que tienen el mismo
> problema.
> **Estimado:** 3 horas (ajuste en facturacion y retiros, con pruebas de ambos flujos).
> cc. @Gerson Barboza Piedra

## B. Nota tecnica para desarrollo

Para quien implemente, o para una sesion nueva de Claude: tiene que poder resolver el ticket sin volver
a investigar. **Sin cc.**

```html
<p><b>Nota tecnica para desarrollo</b></p>
<p><b>Causa raiz:</b> [archivo:linea y mecanismo exacto]</p>
<p>[Solo si aplica — ver references/tipo-bug.md: <b>Es un bug que viene de estandar.</b> [evidencia: git log --all sin commits relacionados / el commit mas viejo del archivo ya lo trae asi]]</p>
<p><b>Cambio propuesto:</b> [que cambiar; copias duplicadas que comparten el defecto y cuales NO]</p>
<p><b>Verificacion post-fix (en Desarrollo):</b></p>
<ol><li>[paso o query, escrito como instruccion]</li></ol>
<p><b>Alcance del analisis:</b> Verificado con evidencia: [...]. Queda por definir al implementar: [...].</p>
```

- La verificacion se escribe como instrucciones; los resultados se comentan despues, cuando exista el
  fix. Se verifica en Desarrollo; al liberar a Staging/UAT solo se corre lo ya validado, salvo que el
  problema sea propio de ese ambiente.
- El parrafo de alcance evita que quien lo tome crea que el analisis es mas completo de lo que es.

## C. Comentario de rechazo o bloqueo

Corto y al grano: la investigacion completa queda en la calibracion, no aqui. Con cc.

```html
<p><b>Revision del caso</b></p>
<p>[Conclusion en una o dos frases: es alcance nuevo / ya se decidio en #NNNN / ya lo gestiona X en otro proyecto / es el comportamiento esperado.]</p>
<p>[Solo si hay decision previa: cita textual, autor, fecha y ticket.]</p>
<p>[La pregunta concreta a negocio, si la hay.]</p>
<p>cc. <a href="#" data-vss-mention="version:2.0,29c2ec0f-5ed2-6b24-b590-3ce280e34d03">@Gerson Barboza Piedra</a> [+ quien indique el usuario]</p>
```

## D. Aviso en otro ticket afectado

```html
<p>El analisis del #[ID] encontro que [una frase de como afecta a este ticket]. El detalle completo esta en ese ticket.</p>
<p>cc. [mencion a Gerson]</p>
```

Mas un link `System.LinkTypes.Related` entre ambos, con el motivo en el comentario del link.

## E. Resumen final para el usuario

```
Ticket #[ID] — [titulo corto]
Decision: [ESTIMAR / RECHAZAR / BLOQUEAR] ([tipo])
Estimado: [N]h · DueDate: mie [fecha] (o "sin fecha: motivo") · ese ciclo queda con [X]h libres
Publicado: [comentario de negocio, nota tecnica, campos, links]
Pendiente: [lo que falta y de quien depende, o "nada"]
```

## Lista de verificacion antes de mostrar un borrador

- [ ] Cada afirmacion tiene evidencia verificada. Lo inferido va marcado como hipotesis o se omite:
      afirmar de mas puede hacer que alguien descarte un bug real como "comportamiento esperado".
- [ ] El comentario de negocio explica la causa, no el sintoma, y no trae archivo:linea.
- [ ] El cc a Gerson esta en los comentarios para negocio (A, C, D) y no en la nota tecnica (B).
- [ ] El estimado del comentario coincide con el que va en los campos.
- [ ] En RECHAZAR/BLOQUEAR no aparece ningun numero de horas.
- [ ] Ningun commit/autor que introdujo el bug aparece en el comentario ni en la nota tecnica — eso
      es solo para el usuario, en el chat (ver `tipo-bug.md`).
