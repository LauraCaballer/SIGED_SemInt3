import React, { useState, useEffect } from "react";
import "../css/Inventario.css";
import ModalEditar from "../Components/ModalEditar";
import ModalArchivar from "../Components/ModalArchivar";
import ModalAgregarProducto from "../Components/ModalAgregarProducto";
import ModalArchivados from "../Components/ModalArchivados";
import { FaBox, FaPlus, FaCheck, FaTimes, FaWeight, FaHashtag, FaTag, FaGem, FaLayerGroup } from "react-icons/fa";
import { MdArchive, MdUnarchive, MdCategory } from "react-icons/md";
import { TbEdit } from "react-icons/tb";
import { BiPackage } from "react-icons/bi";
import { GiGoldBar, GiRecycle } from "react-icons/gi";
import { RiRecycleLine } from "react-icons/ri";
import { apiUrl } from "../config/api";

export default function Inventario() {
  const [prendas, setPrendas] = useState([]);
  const [search, setSearch] = useState("");
  const [filtros, setFiltros] = useState({
    tipoOro: "Todos",
    tipoPrenda: "Todos",
    chatarra: false,
    recuperable: false,
  });

  const [modalEditar, setModalEditar] = useState(null);
  const [modalArchivar, setModalArchivar] = useState(null);
  const [mostrarAgregar, setMostrarAgregar] = useState(false);
  const [mostrarArchivados, setMostrarArchivados] = useState(false);
  const [ordenVisual, setOrdenVisual] = useState("default");

  // Formateo de números (gramos/pesos)
  const formatNumber = (value, decimals = 2) => {
    const num = Number(value || 0);
    if (isNaN(num)) return "0";
    try {
      return num.toLocaleString('es-ES', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
    } catch (e) {
      return num.toFixed(decimals);
    }
  };

  // Estado para ordenamiento de columnas
  const [sortConfig, setSortConfig] = useState({ key: null, direction: null }); // direction: 'asc' | 'desc' | null

  const handleSort = (key) => {
    if (sortConfig.key !== key) {
      setSortConfig({ key, direction: 'asc' });
      return;
    }

    if (sortConfig.direction === 'asc') {
      setSortConfig({ key, direction: 'desc' });
      return;
    }

    // cycle back to default (no sort)
    setSortConfig({ key: null, direction: null });
  };

  const handleChangeOrden = (value) => {
    setOrdenVisual(value);

    if (value === "prediccion") {
      setSortConfig({ key: "demand_score", direction: "desc" });
      return;
    }

    if (value === "stock") {
      setSortConfig({ key: "existencia", direction: "desc" });
      return;
    }

    if (value === "nombre") {
      setSortConfig({ key: "nombre", direction: "asc" });
      return;
    }

    setSortConfig({ key: null, direction: null });
  };

  // 🔹 Cargar datos desde API
  const cargarPrendas = async () => {
    try {
      const res = await fetch(apiUrl("/prendas/prendas/"));
      if (!res.ok) throw new Error("Error al obtener prendas");
      const data = await res.json();
      // preserve original order index so we can return to default ordering
      const visibles = data.filter((p) => !p.archivado).map((p, i) => ({ ...p, _index: i }));
      setPrendas(visibles);
    } catch (err) {
      console.error("Error al obtener prendas:", err);
    }
  };

  useEffect(() => {
    cargarPrendas();
  }, []);

  // Calculamos los totales agrupados solo una vez
  const resumenPorOro = (tipoOro) => {
    const prendasOro = prendas.filter(p => p.tipo_oro_nombre === tipoOro);

    // gramos de prendas (normales: no chatarra ni recuperable)
    const gramosPrendas = prendasOro
      .filter(p => !p.es_chatarra && !p.es_recuperable)
      .reduce((acc, p) => {
        const gramos = parseFloat(p.gramos || 0);
        const existencia = parseFloat(p.existencia || 0);
        return acc + gramos * existencia;
      }, 0);

    const gramosChatarra = prendasOro
      .filter(p => p.es_chatarra)
      .reduce((acc, p) => {
        const gramos = parseFloat(p.gramos || 0);
        const existencia = parseFloat(p.existencia || 0);
        return acc + gramos * existencia;
      }, 0);

    const gramosRecuperable = prendasOro
      .filter(p => p.es_recuperable)
      .reduce((acc, p) => {
        const gramos = parseFloat(p.gramos || 0);
        const existencia = parseFloat(p.existencia || 0);
        return acc + gramos * existencia;
      }, 0);

    const total = gramosPrendas + gramosChatarra + gramosRecuperable;

    return {
      prendas: gramosPrendas.toFixed(2),
      chatarra: gramosChatarra.toFixed(2),
      recuperable: gramosRecuperable.toFixed(2),
      total: total.toFixed(2),
    };
  };

  // Luego en tu JSX:
  const italiano = resumenPorOro("ITALIANO");
  const nacional = resumenPorOro("NACIONAL");

  // Contadores de unidades por tipo de oro
  const unidadesItaliano = prendas.filter(p => p.tipo_oro_nombre === "ITALIANO").length;
  const unidadesNacional = prendas.filter(p => p.tipo_oro_nombre === "NACIONAL").length;

  // 🔹 Filtrado
  const prendasFiltradas = prendas.filter((p) => {
    const cumpleBusqueda = p.nombre.toLowerCase().includes(search.toLowerCase());
    const cumpleOro =
      filtros.tipoOro === "Todos" || p.tipo_oro_nombre === filtros.tipoOro;
    const cumplePrenda =
      filtros.tipoPrenda === "Todos" || p.tipo_prenda_nombre === filtros.tipoPrenda;
    const cumpleChatarra = !filtros.chatarra || p.es_chatarra;
    const cumpleRecuperable = !filtros.recuperable || p.es_recuperable;

    return cumpleBusqueda && cumpleOro && cumplePrenda && cumpleChatarra && cumpleRecuperable;
  });

  // Apply sorting if requested. If no sort, preserve original _index order
  const prendasOrdenadas = [...prendasFiltradas];
  if (sortConfig.key) {
    const { key, direction } = sortConfig;
    prendasOrdenadas.sort((a, b) => {
      let av, bv;
      switch (key) {
        case 'nombre':
          av = (a.nombre || '').toString().toLowerCase();
          bv = (b.nombre || '').toString().toLowerCase();
          return direction === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
        case 'tipo_prenda_nombre':
          av = (a.tipo_prenda_nombre || '').toString().toLowerCase();
          bv = (b.tipo_prenda_nombre || '').toString().toLowerCase();
          return direction === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
        case 'tipo_oro_nombre':
          av = (a.tipo_oro_nombre || '').toString().toLowerCase();
          bv = (b.tipo_oro_nombre || '').toString().toLowerCase();
          return direction === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
        case 'peso':
          // Ordenar por gramos por unidad (no por total)
          av = parseFloat(a.gramos || 0);
          bv = parseFloat(b.gramos || 0);
          return direction === 'asc' ? av - bv : bv - av;
        case 'existencia':
          av = parseFloat(a.existencia || 0);
          bv = parseFloat(b.existencia || 0);
          return direction === 'asc' ? av - bv : bv - av;
        case 'es_chatarra':
          av = a.es_chatarra ? 1 : 0;
          bv = b.es_chatarra ? 1 : 0;
          return direction === 'asc' ? av - bv : bv - av;
        case 'es_recuperable':
          av = a.es_recuperable ? 1 : 0;
          bv = b.es_recuperable ? 1 : 0;
          return direction === 'asc' ? av - bv : bv - av;
        case 'demand_score':
          av = parseFloat(a.demand_score || 0);
          bv = parseFloat(b.demand_score || 0);
          return direction === 'asc' ? av - bv : bv - av;
        default:
          return 0;
      }
    });
  } else {
    // default: preserve original order by _index
    prendasOrdenadas.sort((a, b) => (a._index || 0) - (b._index || 0));
  }

  return (
    <div className="inventario-container">
      <div className="header-inventario">
        <h1 className="text-3xl font-bold text-gray-800">Inventario</h1>
        <div className="header-botones">
          <button onClick={() => setMostrarArchivados(true)} className="btn-archivados btn-flex">
            <MdUnarchive size={19} /> <span>Archivados</span>
          </button>

          <button onClick={() => setMostrarAgregar(true)} className="btn-agregar btn-flex">
            <FaPlus size={16} /> <span>Añadir Producto</span>
          </button>
        </div>
      </div>

      {/* 🔹 Panel de resumen mejorado */}
      <div className="resumen-panel">
        {/* SECCIÓN ITALIANO */}
        <div className="resumen-caja resumen-italiano">
          <div className="resumen-header">
            <h3>Italiano</h3>
          </div>

          <div className="resumen-body">
            <div className="resumen-item">
              <span><FaLayerGroup className="inline mr-1" />Total gramos</span>
              <strong>{formatNumber(italiano.total, 2)} g</strong>
            </div>

            <div className="resumen-item">
              <span><GiGoldBar className="inline mr-1" />Oro</span>
              <strong>{formatNumber(italiano.prendas, 2)} g</strong>
            </div>

            <div className="resumen-item">
              <span><GiRecycle className="inline mr-1" />Chatarra</span>
              <strong>{formatNumber(italiano.chatarra, 2)} g</strong>
            </div>

            <div className="resumen-item">
              <span><RiRecycleLine className="inline mr-1" />Recuperable</span>
              <strong>{formatNumber(italiano.recuperable, 2)} g</strong>
            </div>
          </div>
        </div>

        {/* SECCIÓN NACIONAL */}
        <div className="resumen-caja resumen-nacional">
          <div className="resumen-header">
            <h3>Nacional</h3>
          </div>

          <div className="resumen-body">
            <div className="resumen-item">
              <span><FaLayerGroup className="inline mr-1" />Total gramos</span>
              <strong>{formatNumber(nacional.total, 2)} g</strong>
            </div>

            <div className="resumen-item">
              <span><GiGoldBar className="inline mr-1" />Oro</span>
              <strong>{formatNumber(nacional.prendas, 2)} g</strong>
            </div>

            <div className="resumen-item">
              <span><GiRecycle className="inline mr-1" />Chatarra</span>
              <strong>{formatNumber(nacional.chatarra, 2)} g</strong>
            </div>

            <div className="resumen-item">
              <span><RiRecycleLine className="inline mr-1" />Recuperable</span>
              <strong>{formatNumber(nacional.recuperable, 2)} g</strong>
            </div>
          </div>
        </div>

        {/* SECCIÓN GENERAL */}
        <div className="resumen-caja resumen-general">
          <div className="resumen-header">
            <h3>General</h3>
          </div>

          <div className="resumen-body">
            <div className="resumen-item">
              <span><BiPackage className="inline mr-1" />Productos</span>
              <strong>{prendas.length}</strong>
            </div>

            <div className="resumen-item">
              <span><FaGem className="inline mr-1" style={{color: '#FFD700'}} />Italiano (unidades)</span>
              <strong>{unidadesItaliano}</strong>
            </div>

            <div className="resumen-item">
              <span><FaGem className="inline mr-1" style={{color: '#6B8EAD'}} />Nacional (unidades)</span>
              <strong>{unidadesNacional}</strong>
            </div>

            <div className="resumen-item">
                <span><FaWeight className="inline mr-1" />Gramos totales</span>
                <strong>
                  {formatNumber(
                    prendas.reduce((acc, p) => {
                      const gramos = parseFloat(p.gramos || 0);
                      const existencia = parseFloat(p.existencia || 0);
                      return acc + gramos * existencia;
                    }, 0),
                    2
                  )} g
                </strong>
            </div>
          </div>
        </div>
      </div>

      {/* 🔍 Buscador */}
      <input
        type="text"
        placeholder="Buscar prenda..."
        className="inventario-busqueda"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {/* 🔽 Filtros mejorados */}
      <div className="inventario-filtros">
        <div className="filtro-grupo">
          <label>Tipo Oro:</label>
          <select
            value={filtros.tipoOro}
            onChange={(e) => setFiltros({ ...filtros, tipoOro: e.target.value })}
            className={`filtro-select ${
              filtros.tipoOro === "ITALIANO" ? "filtro-italiano" :
              filtros.tipoOro === "NACIONAL" ? "filtro-nacional" : ""
            }`}
          >
            <option>Todos</option>
            <option>ITALIANO</option>
            <option>NACIONAL</option>
          </select>
        </div>

        <div className="filtro-grupo">
          <label>Tipo Prenda:</label>
          <select
            value={filtros.tipoPrenda}
            onChange={(e) => setFiltros({ ...filtros, tipoPrenda: e.target.value })}
            className="filtro-select filtro-prenda"
          >
            <option>Todos</option>
            {[...new Set(prendas.map((p) => p.tipo_prenda_nombre))].map((tp) => (
              <option key={tp}>{tp}</option>
            ))}
          </select>
        </div>

        <div className="filtro-checkbox chatarra">
          <label>Chatarra</label>
          <input
            type="checkbox"
            checked={filtros.chatarra}
            onChange={(e) => {
              const checked = e.target.checked;
              if (checked && filtros.recuperable) {
                alert("No puede seleccionar 'Chatarra' y 'Recuperable' al mismo tiempo.");
                return;
              }
              setFiltros({ ...filtros, chatarra: checked });
            }}
          />
        </div>

        <div className="filtro-checkbox recuperable">
          <label>Recuperable</label>
          <input
            type="checkbox"
            checked={filtros.recuperable}
            onChange={(e) => {
              const checked = e.target.checked;
              if (checked && filtros.chatarra) {
                alert("No puede seleccionar 'Chatarra' y 'Recuperable' al mismo tiempo.");
                return;
              }
              setFiltros({ ...filtros, recuperable: checked });
            }}
          />
        </div>

        <div className="filtro-grupo">
          <label>Ordenar por:</label>
          <select
            value={ordenVisual}
            onChange={(e) => handleChangeOrden(e.target.value)}
            className="filtro-select filtro-prenda"
          >
            <option value="default">Orden original</option>
            <option value="prediccion">Más probables de comprar</option>
            <option value="stock">Mayor stock</option>
            <option value="nombre">Nombre A-Z</option>
          </select>
        </div>
      </div>

      {/* 🧾 Tabla */}
      <table className="inventario-tabla">
        <thead>
          <tr>
            <th onClick={() => handleSort('nombre')} className="cursor-pointer"><BiPackage className="inline mr-1" />Producto {sortConfig.key==='nombre' && (sortConfig.direction==='asc' ? '▲' : sortConfig.direction==='desc' ? '▼' : '')}</th>
            <th onClick={() => handleSort('tipo_prenda_nombre')} className="cursor-pointer"><MdCategory className="inline mr-1" />Categoría {sortConfig.key==='tipo_prenda_nombre' && (sortConfig.direction==='asc' ? '▲' : sortConfig.direction==='desc' ? '▼' : '')}</th>
            <th onClick={() => handleSort('tipo_oro_nombre')} className="cursor-pointer"><FaGem className="inline mr-1" />Material {sortConfig.key==='tipo_oro_nombre' && (sortConfig.direction==='asc' ? '▲' : sortConfig.direction==='desc' ? '▼' : '')}</th>
            <th onClick={() => handleSort('peso')} className="cursor-pointer"><FaWeight className="inline mr-1" />Peso {sortConfig.key==='peso' && (sortConfig.direction==='asc' ? '▲' : sortConfig.direction==='desc' ? '▼' : '')}</th>
            <th onClick={() => handleSort('existencia')} className="cursor-pointer"><FaHashtag className="inline mr-1" />Cantidad {sortConfig.key==='existencia' && (sortConfig.direction==='asc' ? '▲' : sortConfig.direction==='desc' ? '▼' : '')}</th>
            <th onClick={() => handleSort('demand_score')} className="cursor-pointer"><FaLayerGroup className="inline mr-1" />Predicción {sortConfig.key==='demand_score' && (sortConfig.direction==='asc' ? '▲' : sortConfig.direction==='desc' ? '▼' : '')}</th>
            <th>Recomendación</th>
            <th onClick={() => handleSort('es_chatarra')} className="cursor-pointer"><FaTag className="inline mr-1" />Chatarra {sortConfig.key==='es_chatarra' && (sortConfig.direction==='asc' ? '▲' : sortConfig.direction==='desc' ? '▼' : '')}</th>
            <th onClick={() => handleSort('es_recuperable')} className="cursor-pointer"><FaTag className="inline mr-1" />Recuperable {sortConfig.key==='es_recuperable' && (sortConfig.direction==='asc' ? '▲' : sortConfig.direction==='desc' ? '▼' : '')}</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {prendasOrdenadas.map((p) => (
            <tr key={p.id}>
              <td>{p.nombre}</td>
              <td>{p.tipo_prenda_nombre}</td>
              <td>{p.tipo_oro_nombre}</td>
              <td>{formatNumber(parseFloat(p.gramos || 0), 2)} g</td>
              <td className={p.existencia > 0 ? "cantidad-verde" : "cantidad-roja"}>
                {p.existencia}
              </td>
              <td>{formatNumber(p.demand_score || 0, 2)}</td>
              <td>{p.demand_recomendacion || "→ Mantener"}</td>
              <td>
                {p.es_chatarra ? (
                  <FaCheck size={16} color="#0a9300" className="icon-verde" />
                ) : (
                  <FaTimes size={16} color="#c40000" className="icon-rojo" />
                )}
              </td>

              <td>
                {p.es_recuperable ? (
                  <FaCheck size={16} color="#0a9300" className="icon-verde" />
                ) : (
                  <FaTimes size={16} color="#c40000" className="icon-rojo" />
                )}
              </td>

              <td>
                <button
                  className="btn-editar btn-flex"
                  onClick={() => setModalEditar(p)}
                >
                  <TbEdit size={16} />
                </button>

                <button
                  className="btn-archivar btn-flex"
                  onClick={() => setModalArchivar(p)}
                >
                  <MdArchive size={19} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {modalEditar && (
        <ModalEditar
          prenda={modalEditar}
          onClose={() => setModalEditar(null)}
          onSaved={cargarPrendas}
        />
      )}

      {modalArchivar && (
        <ModalArchivar
          prenda={modalArchivar}
          onClose={() => setModalArchivar(null)}
          onArchived={cargarPrendas}
        />
      )}

      {mostrarAgregar && (
        <ModalAgregarProducto
          onClose={() => setMostrarAgregar(false)}
          onAdd={() => window.location.reload()}
        />
      )}

      {mostrarArchivados && (
        <ModalArchivados
          onClose={() => setMostrarArchivados(false)}
          onRefresh={() => window.location.reload()}
        />
      )}
    </div>
  );
}
