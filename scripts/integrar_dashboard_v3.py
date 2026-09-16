# -*- coding: utf-8 -*-

"""
======================================================================
SALUDDATA STEM
Integración del Explorador V3 en el Dashboard

¿QUÉ HACE?
-----------
Integra un panel interactivo de filtros en el dashboard existente.

¿CÓMO?
------
1. Conserva el dashboard V2.
2. Inserta un panel de filtros después del selector de fuentes.
3. Agrega estilos específicos para el panel.
4. Agrega JavaScript para consultar:
       /api/explorer/options
       /api/explorer/query
5. Reutiliza los gráficos existentes de Plotly.
6. Mantiene la API V1 y la API V3 intactas.

¿POR QUÉ?
----------
Queremos evolucionar el dashboard sin reconstruirlo desde cero.

¿CONCEPTO STEM?
----------------
Exploración de datos:
datos → filtros → consulta → transformación → visualización → interpretación

NOTA
----
El script crea una copia adicional antes de modificar el dashboard.
La integración se identifica mediante el marcador:

    SALUDDATA_V3_INTEGRATION

======================================================================
"""

from pathlib import Path
import shutil


# ---------------------------------------------------------------------
# RUTAS DEL PROYECTO
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

DASHBOARD = ROOT / "app" / "templates" / "dashboard.html"

BACKUP = ROOT / "app" / "templates" / "dashboard_v2_pre_v3.html"


# ---------------------------------------------------------------------
# MARCADOR DE SEGURIDAD
# ---------------------------------------------------------------------

MARKER = "SALUDDATA_V3_INTEGRATION"


# ---------------------------------------------------------------------
# PANEL HTML
# ---------------------------------------------------------------------

FILTER_PANEL = r'''
<!-- ================================================================
     SALUDDATA STEM · EXPLORADOR V3
     ================================================================ -->

<section class="v3-explorer" id="v3-explorer">

    <div class="v3-explorer-header">

        <div>
            <span class="v2-kicker">
                EXPLORACIÓN INTERACTIVA
            </span>

            <h2>
                Explore los datos
            </h2>

            <p>
                Seleccione criterios para construir una consulta
                específica sobre la fuente activa.
            </p>
        </div>

        <div class="v3-status" id="v3-status">
            Consulta general
        </div>

    </div>


    <div class="v3-filter-grid">

        <!-- AÑO -->

        <label class="v3-filter">

            <span>
                Año
            </span>

            <select id="filter-year">
                <option value="">
                    Todos los años
                </option>
            </select>

        </label>


        <!-- SEXO -->

        <label class="v3-filter">

            <span>
                Sexo
            </span>

            <select id="filter-sex">
                <option value="">
                    Todos
                </option>
            </select>

        </label>


        <!-- LOCALIDAD -->

        <label class="v3-filter">

            <span>
                Localidad
            </span>

            <select id="filter-locality">
                <option value="">
                    Todas las localidades
                </option>
            </select>

        </label>


        <!-- GRUPO DE EDAD -->

        <label class="v3-filter">

            <span>
                Grupo de edad
            </span>

            <select id="filter-age">
                <option value="">
                    Todos los grupos
                </option>
            </select>

        </label>


        <!-- CAUSA -->

        <label class="v3-filter">

            <span>
                Causa
            </span>

            <select id="filter-cause">
                <option value="">
                    Todas las causas
                </option>
            </select>

        </label>

    </div>


    <div class="v3-filter-actions">

        <button
            type="button"
            class="v3-btn v3-btn-primary"
            id="btn-apply-filters">

            Aplicar filtros

        </button>


        <button
            type="button"
            class="v3-btn v3-btn-secondary"
            id="btn-clear-filters">

            Limpiar

        </button>

    </div>


    <div
        class="v3-active-filters"
        id="v3-active-filters">

        Sin filtros activos

    </div>

</section>


<style>
/* ================================================================
   SALUDDATA STEM · ESTILOS DEL EXPLORADOR V3
   ================================================================ */

.v3-explorer {
    margin: 28px 0;
    padding: 28px;
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 22px;
    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,.045),
            rgba(255,255,255,.018)
        );
    box-shadow:
        0 18px 50px rgba(0,0,0,.18);
}

.v3-explorer-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 24px;
    margin-bottom: 24px;
}

.v3-explorer-header h2 {
    margin: 7px 0 6px;
}

.v3-explorer-header p {
    margin: 0;
    max-width: 760px;
    opacity: .72;
}

.v3-status {
    flex-shrink: 0;
    padding: 9px 14px;
    border-radius: 999px;
    border: 1px solid rgba(0,245,255,.25);
    background: rgba(0,245,255,.055);
    font-size: .78rem;
    letter-spacing: .04em;
}

.v3-filter-grid {
    display: grid;
    grid-template-columns:
        repeat(5, minmax(150px, 1fr));
    gap: 14px;
}

.v3-filter {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.v3-filter > span {
    font-size: .74rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    opacity: .7;
}

.v3-filter select {
    width: 100%;
    min-height: 44px;
    padding: 10px 12px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,.10);
    background: rgba(4,9,20,.85);
    color: inherit;
    outline: none;
}

.v3-filter select:focus {
    border-color: rgba(0,245,255,.45);
    box-shadow: 0 0 0 3px rgba(0,245,255,.07);
}

.v3-filter-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 20px;
}

.v3-btn {
    min-height: 42px;
    padding: 10px 18px;
    border-radius: 11px;
    border: 1px solid transparent;
    cursor: pointer;
    font: inherit;
    font-weight: 700;
    transition:
        transform .18s ease,
        opacity .18s ease,
        border-color .18s ease;
}

.v3-btn:hover {
    transform: translateY(-1px);
}

.v3-btn:disabled {
    opacity: .5;
    cursor: wait;
}

.v3-btn-primary {
    background: rgba(0,245,255,.13);
    border-color: rgba(0,245,255,.35);
    color: inherit;
}

.v3-btn-secondary {
    background: rgba(255,255,255,.045);
    border-color: rgba(255,255,255,.10);
    color: inherit;
}

.v3-active-filters {
    margin-top: 16px;
    padding-top: 14px;
    border-top: 1px solid rgba(255,255,255,.07);
    font-size: .82rem;
    opacity: .72;
}

@media (max-width: 1050px) {

    .v3-filter-grid {
        grid-template-columns:
            repeat(2, minmax(180px, 1fr));
    }

}

@media (max-width: 620px) {

    .v3-explorer {
        padding: 20px;
    }

    .v3-explorer-header {
        flex-direction: column;
    }

    .v3-filter-grid {
        grid-template-columns: 1fr;
    }

}
</style>
'''


# ---------------------------------------------------------------------
# JAVASCRIPT V3
# ---------------------------------------------------------------------

V3_SCRIPT = r'''
/* ================================================================
   SALUDDATA STEM · CAPA DE INTERACCIÓN V3
   ================================================================ */

/*
======================================================================
ESTADO DEL EXPLORADOR
======================================================================

¿Qué hace?
-----------
Mantiene separado el estado del explorador del estado visual
original del dashboard.

¿Por qué?
----------
Esto permite cambiar de fuente y aplicar filtros sin reconstruir
los gráficos desde cero.
======================================================================
*/

let explorerData = null;


/*
======================================================================
OBTENER OPCIONES
======================================================================

Consulta las categorías disponibles para la fuente activa.

Endpoint:
    /api/explorer/options?dataset=...

======================================================================
*/

async function cargarOpcionesV3() {

    const response = await fetch(
        `/api/explorer/options?dataset=${encodeURIComponent(activeDataset)}`
    );

    if (!response.ok) {

        throw new Error(
            "No fue posible obtener las opciones del explorador."
        );

    }

    const payload = await response.json();

    if (
        payload.status !== "ok" ||
        !payload.options
    ) {

        throw new Error(
            "La API de opciones devolvió una estructura inválida."
        );

    }

    return payload.options;

}


/*
======================================================================
POBLAR SELECT
======================================================================

¿Qué hace?
-----------
Carga dinámicamente un <select>.

Esto evita escribir manualmente localidades, años, causas o edades.

======================================================================
*/

function poblarSelect(
    id,
    values,
    placeholder
) {

    const select =
        document.getElementById(id);

    select.innerHTML = "";

    const defaultOption =
        document.createElement("option");

    defaultOption.value = "";
    defaultOption.textContent = placeholder;

    select.appendChild(
        defaultOption
    );


    (values || []).forEach(
        value => {

            const option =
                document.createElement("option");

            option.value = value;
            option.textContent = value;

            select.appendChild(
                option
            );

        }
    );

}


/*
======================================================================
CARGAR FILTROS V3
======================================================================
*/

async function prepararFiltrosV3() {

    const options =
        await cargarOpcionesV3();


    poblarSelect(
        "filter-year",
        options.years,
        "Todos los años"
    );


    poblarSelect(
        "filter-sex",
        options.sex,
        "Todos"
    );


    poblarSelect(
        "filter-locality",
        options.locality,
        "Todas las localidades"
    );


    poblarSelect(
        "filter-age",
        options.age_group,
        "Todos los grupos"
    );


    poblarSelect(
        "filter-cause",
        options.cause,
        "Todas las causas"
    );

}


/*
======================================================================
LEER FILTROS
======================================================================
*/

function obtenerFiltrosV3() {

    return {

        year:
            document.getElementById(
                "filter-year"
            ).value,

        sex:
            document.getElementById(
                "filter-sex"
            ).value,

        locality:
            document.getElementById(
                "filter-locality"
            ).value,

        age_group:
            document.getElementById(
                "filter-age"
            ).value,

        cause:
            document.getElementById(
                "filter-cause"
            ).value

    };

}


/*
======================================================================
CONSTRUIR CONSULTA
======================================================================
*/

function construirQueryV3(
    filters
) {

    const params =
        new URLSearchParams();


    params.set(
        "dataset",
        activeDataset
    );


    Object.entries(filters).forEach(
        ([key, value]) => {

            if (
                value !== null &&
                value !== undefined &&
                value !== ""
            ) {

                params.set(
                    key,
                    value
                );

            }

        }
    );


    return params.toString();

}


/*
======================================================================
ACTUALIZAR TEXTO DE FILTROS
======================================================================
*/

function actualizarEstadoFiltrosV3(
    filters
) {

    const active =
        document.getElementById(
            "v3-active-filters"
        );

    const status =
        document.getElementById(
            "v3-status"
        );


    const labels = {

        year: "Año",
        sex: "Sexo",
        locality: "Localidad",
        age_group: "Edad",
        cause: "Causa"

    };


    const entries =
        Object.entries(filters)
            .filter(
                ([, value]) =>
                    value !== null &&
                    value !== undefined &&
                    value !== ""
            );


    if (!entries.length) {

        active.textContent =
            "Sin filtros activos";

        status.textContent =
            "Consulta general";

        return;

    }


    active.textContent =
        "Filtros activos: " +
        entries
            .map(
                ([key, value]) =>
                    `${labels[key]}: ${value}`
            )
            .join(" · ");


    status.textContent =
        `${entries.length} filtro(s) activo(s)`;

}


/*
======================================================================
CONSULTAR EXPLORADOR
======================================================================

¿Qué hace?
-----------
Envía los filtros seleccionados al backend.

¿Qué recibe?
-------------
La API devuelve exactamente:

    records
    value
    temporal
    locality
    sex
    age_group
    cause
    filters

Por tanto, podemos reutilizar directamente los gráficos V2.

======================================================================
*/

async function ejecutarConsultaV3(
    filters = obtenerFiltrosV3()
) {

    const button =
        document.getElementById(
            "btn-apply-filters"
        );


    button.disabled = true;
    button.textContent =
        "Consultando...";


    try {

        const query =
            construirQueryV3(
                filters
            );


        const response =
            await fetch(
                `/api/explorer/query?${query}`
            );


        if (!response.ok) {

            throw new Error(
                "La consulta del explorador no pudo completarse."
            );

        }


        const payload =
            await response.json();


        if (
            payload.status !== "ok" ||
            !payload.data
        ) {

            throw new Error(
                payload.message ||
                "La API devolvió una respuesta inválida."
            );

        }


        explorerData =
            payload.data;


        /*
        --------------------------------------------------------------
        CONECTAR V3 CON LOS GRÁFICOS V2
        --------------------------------------------------------------

        Los gráficos existentes esperan:

            dashboardData[activeDataset]

        Por eso no los reconstruimos.

        Simplemente sustituimos temporalmente la fuente de datos
        por el resultado filtrado.
        --------------------------------------------------------------
        */

        dashboardData = {

            [activeDataset]:
                explorerData

        };


        actualizarEstadoFiltrosV3(
            filters
        );


        await actualizarResumenV3();


        dibujarTemporal();
        dibujarTerritorio();
        dibujarSexo();
        dibujarEdad();
        dibujarCausas();


    }
    finally {

        button.disabled = false;

        button.textContent =
            "Aplicar filtros";

    }

}


/*
======================================================================
ACTUALIZAR RESUMEN V3
======================================================================

Utiliza los resultados reales de la consulta.

Esto permite que los indicadores cambien al aplicar filtros.

======================================================================
*/

async function actualizarResumenV3() {

    if (!explorerData) {

        return;

    }


    const config =
        DATASET_CONFIG[
            activeDataset
        ];


    document.getElementById(
        "active-title"
    ).textContent =
        config.title;


    document.getElementById(
        "active-description"
    ).textContent =
        config.description;


    document.getElementById(
        "stat-records"
    ).textContent =
        numero(
            explorerData.records
        );


    document.getElementById(
        "stat-periods"
    ).textContent =
        numero(
            explorerData.temporal
                ? explorerData.temporal.length
                : 0
        );


    document.getElementById(
        "stat-localities"
    ).textContent =
        numero(
            explorerData.locality
                ? explorerData.locality.length
                : 0
        );


    document.getElementById(
        "stat-causes"
    ).textContent =
        numero(
            explorerData.cause
                ? explorerData.cause.length
                : 0
        );

}


/*
======================================================================
LIMPIAR FILTROS
======================================================================
*/

async function limpiarFiltrosV3() {

    document.getElementById(
        "filter-year"
    ).value = "";


    document.getElementById(
        "filter-sex"
    ).value = "";


    document.getElementById(
        "filter-locality"
    ).value = "";


    document.getElementById(
        "filter-age"
    ).value = "";


    document.getElementById(
        "filter-cause"
    ).value = "";


    const filters =
        obtenerFiltrosV3();


    await ejecutarConsultaV3(
        filters
    );

}


/*
======================================================================
CAMBIO DE DATASET
======================================================================

Cada fuente posee sus propias categorías.

Por ejemplo:

Cardiovascular:
    1 causa

Respiratorio:
    5 causas

Mortalidad:
    220 causas

Por eso debemos volver a consultar /options cada vez que
cambia la fuente.

======================================================================
*/

async function cambiarDatasetV3(
    dataset
) {

    activeDataset =
        dataset;


    await prepararFiltrosV3();


    /*
    Al cambiar de fuente se comienza con una consulta general.
    */

    await ejecutarConsultaV3(
        {
            year: "",
            sex: "",
            locality: "",
            age_group: "",
            cause: ""
        }
    );

}


/*
======================================================================
EVENTOS V3
======================================================================
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const applyButton =
            document.getElementById(
                "btn-apply-filters"
            );


        const clearButton =
            document.getElementById(
                "btn-clear-filters"
            );


        if (applyButton) {

            applyButton.addEventListener(
                "click",
                async () => {

                    try {

                        await ejecutarConsultaV3();

                    }
                    catch (error) {

                        console.error(
                            error
                        );

                        alert(
                            error.message
                        );

                    }

                }
            );

        }


        if (clearButton) {

            clearButton.addEventListener(
                "click",
                async () => {

                    try {

                        await limpiarFiltrosV3();

                    }
                    catch (error) {

                        console.error(
                            error
                        );

                        alert(
                            error.message
                        );

                    }

                }
            );

        }


        /*
        --------------------------------------------------------------
        CAMBIO DE FUENTE
        --------------------------------------------------------------
        */

        document
            .querySelectorAll(
                ".v2-tab"
            )
            .forEach(
                button => {

                    button.addEventListener(
                        "click",
                        async () => {

                            document
                                .querySelectorAll(
                                    ".v2-tab"
                                )
                                .forEach(
                                    item =>
                                        item.classList.remove(
                                            "active"
                                        )
                                );


                            button.classList.add(
                                "active"
                            );


                            try {

                                await cambiarDatasetV3(
                                    button.dataset.dataset
                                );

                            }
                            catch (error) {

                                console.error(
                                    error
                                );

                                alert(
                                    error.message
                                );

                            }

                        }
                    );

                }
            );

    }
);


/*
======================================================================
SUSTITUIR EL FLUJO DE ACTUALIZACIÓN V2
======================================================================

La función original actualiza los gráficos utilizando
/api/analytics.

V3 utiliza el explorador.

No eliminamos la función original del archivo:
simplemente reemplazamos la referencia utilizada durante esta
ejecución.

======================================================================
*/

actualizarDashboard =
    async function () {

        await prepararFiltrosV3();


        await ejecutarConsultaV3(
            {
                year: "",
                sex: "",
                locality: "",
                age_group: "",
                cause: ""
            }
        );

    };


/*
======================================================================
FIN DE INTEGRACIÓN V3
======================================================================
*/
'''


# ---------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ---------------------------------------------------------------------

def main():
    """
    Ejecuta la integración V3 de manera segura.
    """

    print("=" * 70)
    print("SALUDDATA STEM - INTEGRACIÓN DASHBOARD V3")
    print("=" * 70)

    if not DASHBOARD.exists():

        raise FileNotFoundError(
            f"No se encontró el dashboard:\n{DASHBOARD}"
        )


    original = DASHBOARD.read_text(
        encoding="utf-8"
    )


    # ---------------------------------------------------------------
    # Evitar aplicar dos veces la misma integración.
    # ---------------------------------------------------------------

    if MARKER in original:

        print()
        print("AVISO: La integración V3 ya existe.")
        print("No se realizaron cambios.")
        return


    # ---------------------------------------------------------------
    # Crear respaldo.
    # ---------------------------------------------------------------

    shutil.copy2(
        DASHBOARD,
        BACKUP
    )

    print()
    print(f"Respaldo creado:")
    print(f"  {BACKUP}")


    # ---------------------------------------------------------------
    # Localizar el selector de fuentes.
    # ---------------------------------------------------------------

    selector_marker = '<section class="v2-source-selector">'

    selector_position = original.find(
        selector_marker
    )

    if selector_position == -1:

        raise RuntimeError(
            "No fue posible localizar el selector de fuentes V2."
        )


    selector_end = original.find(
        "</section>",
        selector_position
    )

    if selector_end == -1:

        raise RuntimeError(
            "No fue posible localizar el cierre del selector V2."
        )

    selector_end += len("</section>")


    # ---------------------------------------------------------------
    # Insertar panel V3 inmediatamente después del selector.
    # ---------------------------------------------------------------

    modified = (
        original[:selector_end]
        + "\n\n"
        + FILTER_PANEL
        + "\n"
        + original[selector_end:]
    )


    # ---------------------------------------------------------------
    # Insertar JavaScript antes del cierre del script principal.
    # ---------------------------------------------------------------

    script_end = modified.rfind(
        "</script>"
    )

    if script_end == -1:

        raise RuntimeError(
            "No fue posible localizar </script>."
        )


    v3_block = (
        "\n\n<!-- "
        + MARKER
        + " -->\n"
        + V3_SCRIPT
        + "\n"
    )


    # ---------------------------------------------------------------
    # Insertar JavaScript V3 en el dashboard.
    # ---------------------------------------------------------------

    modified = (
        modified[:script_end]
        + v3_block
        + modified[script_end:]
    )
    

    # ---------------------------------------------------------------
    # Guardar.
    # ---------------------------------------------------------------

    DASHBOARD.write_text(
        modified,
        encoding="utf-8",
        newline=""
    )


    print()
    print("Integración V3 aplicada correctamente.")
    print()
    print(f"Dashboard:")
    print(f"  {DASHBOARD}")
    print()
    print(f"Respaldo:")
    print(f"  {BACKUP}")
    print()
    print("Codificación: UTF-8")
    print("Marcador: SALUDDATA_V3_INTEGRATION")
    print()
    print("=" * 70)
    print("SIGUIENTE PASO")
    print("=" * 70)
    print()
    print("Ejecute:")
    print()
    print("python -m py_compile app\\templates\\dashboard.html")
    print()
    print("NOTA: ese comando NO valida HTML.")
    print("La validación real se realizará con Flask + navegador.")
    print()


if __name__ == "__main__":
    main()