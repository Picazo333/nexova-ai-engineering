# Company Choice — Nexova Solutions

## Selected Company

**Nexova Solutions**

## Why I Chose This Company

Elegí Nexova porque combina problemas centrales de negocio con oportunidades de AI Engineering que pueden reutilizarse fuera del contexto académico. Su operación depende de procesos todavía manuales en selección, ventas, soporte, formación y reporting, mientras que el briefing plantea explícitamente soluciones como scoring y ranking de CVs, búsqueda semántica, RAG, automatización comercial y agentes de IA. También ofrece una alta transferibilidad: patrones como lead qualification, knowledge retrieval, entity matching, support automation y executive intelligence aparecen en muchas empresas B2B y pueden abstraerse en componentes reutilizables. Frente a las otras opciones, Nexova ofrece un equilibrio especialmente fuerte entre profundidad técnica, valor de portafolio y posibilidad de convertir parte del trabajo del curso en activos aplicables a proyectos o servicios reales. Por ello, la elección busca que las 24 semanas produzcan simultáneamente aprendizaje acumulativo y software con potencial de reutilización y monetización.

## Decision Framework

La decisión se tomó después de comparar las cuatro compañías — Brasaland, HealthCore, Nexova y TrackFlow — mediante una matriz ponderada. Los factores de mayor peso fueron la transferencia directa a negocios reales, el potencial de automatizaciones avanzadas y el **Economic Learning Leverage**: la capacidad de convertir lo aprendido en componentes, productos o servicios que puedan generar uso real, feedback y eventualmente recursos para financiar una mayor profundidad técnica. TrackFlow resultó superior en complejidad operativa intrínseca, pero Nexova obtuvo el mejor valor compuesto por su reutilización horizontal, compatibilidad con arquitecturas agentic y menor distancia entre coursework y aplicación comercial.

## Departments That Interest Me

### Sales and Business Development

El equipo comercial tiene HubSpot, pero su uso es inconsistente; la prospección y el seguimiento siguen siendo mayormente manuales y se pierden oportunidades por falta de actividad. Me interesa porque permite combinar CRM, automatización de secuencias, scoring, alertas y un agente que utilice contexto del prospecto, servicios, pricing y políticas comerciales para recomendar el siguiente mejor paso. Es un caso de alto valor porque el mismo patrón puede reutilizarse en muchas operaciones B2B.

### Recruitment Operations

Es el núcleo del negocio de Nexova y actualmente cada consultor revisa manualmente entre 30 y 80 CVs por proceso. El briefing propone scoring y ranking automático, RAG sobre la base de candidatos, visibilidad en tiempo real del proceso y comunicación automatizada. Me interesa porque permite trabajar con extracción estructurada, filtros determinísticos, semantic search, embeddings, reranking, explainability, evaluación y human-in-the-loop sobre una operación directamente ligada a los ingresos de la empresa.

### Customer Support

El equipo trabaja sin una base de conocimiento centralizada y tiene un tiempo medio de resolución de 48 horas frente a un SLA comprometido de 24 horas. El objetivo de resolver una parte relevante de las consultas mediante RAG y automatización permite diseñar un sistema medible, con confidence thresholds, escalamiento, observabilidad y supervisión humana.

## Automation Challenge

Un reto especialmente atractivo es construir el **pipeline de selección asistido por IA**. La solución debe transformar una descripción de vacante en requisitos estructurados, aplicar filtros duros cuando corresponda, recuperar candidatos mediante búsqueda híbrida, ordenarlos con scoring explicable y presentar evidencia suficiente para que el consultor valide el ranking. El objetivo no es sustituir el criterio profesional, sino reducir trabajo repetitivo y hacer el matching más consistente, auditable y rápido.

## My AI Agent Idea

Propongo un **Sales Opportunity Agent** para el equipo de Ventas y Desarrollo de Negocio.

**Qué hace:** analiza cada oportunidad activa y recomienda el ángulo comercial y el siguiente mejor paso, utilizando el contexto disponible en el CRM y las reglas reales de Nexova. Puede sugerir un servicio, preparar un argumento, proponer un seguimiento y redactar una comunicación, pero las acciones sujetas a políticas o aprobación permanecen bajo controles determinísticos y supervisión humana.

**Inputs principales:**
- Datos del prospecto y de la empresa.
- Industria y contexto comercial.
- Historial de conversaciones y actividad en HubSpot.
- Líneas de servicio de Nexova.
- Modelo de precios.
- Políticas de manejo de objeciones.
- Estado actual del deal.

**Outputs / acciones:**
- Servicio recomendado.
- Ángulo de propuesta.
- Razón y evidencia utilizada.
- Siguiente mejor acción.
- Borrador de seguimiento.
- Fecha sugerida de próxima actividad.
- Señal de aprobación humana cuando una regla comercial lo exija.

La arquitectura se diseñaría separando el núcleo reutilizable — agregación de contexto, retrieval, recommendation, policy checks y tool interfaces — de la configuración específica de Nexova. Esto permitiría evaluar posteriormente su viabilidad como un **Opportunity Intelligence Engine** aplicable a otros negocios B2B.
