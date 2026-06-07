import React from "react";
import { FaPhone, FaEnvelope, FaIdCard, FaMapMarkerAlt, FaChartLine, FaCalendarAlt, FaBoxes } from "react-icons/fa";

// Función para formatear números al estándar español: 53.189,90
const formatNumber = (value, decimals = 2) => {
  if (!value && value !== 0) return '';
  const num = parseFloat(value);
  if (isNaN(num)) return '';
  return num.toLocaleString('es-ES', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

const ClientDetail = ({ cliente, historial }) => {
  if (!cliente) {
    return (
      <div className="p-6 text-gray-500 italic">
        Selecciona un cliente para ver los detalles.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6 w-full">
      {/* Encabezado */}
      <h2 className="text-2xl font-semibold text-gray-800 mb-4 text-center">
        Detalles del Cliente
      </h2>

      {/* Información personal */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <p className="text-gray-600 flex items-center gap-2">
            <FaIdCard className="text-purple-600" />
            <span className="font-medium">Cédula:</span> {cliente.cedula}
          </p>
          <p className="text-gray-600 flex items-center gap-2 mt-2">
            <FaPhone className="text-purple-600" />
            <span className="font-medium">Teléfono:</span>
            {cliente.telefono || "No registrado"}
          </p>
          <p className="text-gray-600 flex items-center gap-2 mt-2">
            <FaEnvelope className="text-purple-600" />
            <span className="font-medium">Correo:</span>
            {cliente.email || "No registrado"}
          </p>
        </div>

        <div>
          <p className="text-gray-600 flex items-center gap-2">
            <FaMapMarkerAlt className="text-purple-600" />
            <span className="font-medium">Dirección:</span>
            {cliente.direccion || "No registrada"}
          </p>
        </div>
      </div>

      {/* Predicción */}
      <div className="border border-gray-200 rounded-lg p-4 bg-gray-50 mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <FaChartLine className="text-purple-600" />
          Predicción del cliente
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-lg bg-white border border-gray-200 p-3">
            <p className="text-xs uppercase text-gray-500 mb-1">Score RFM</p>
            <strong className="text-2xl text-gray-800">
              {formatNumber(cliente.rfm_score || 0, 2)}
            </strong>
            <p className="text-sm text-gray-600 mt-1">{cliente.probabilidad_compra || "Baja"}</p>
          </div>

          <div className="rounded-lg bg-white border border-gray-200 p-3">
            <p className="text-xs uppercase text-gray-500 mb-1 flex items-center gap-1">
              <FaCalendarAlt /> Próxima compra
            </p>
            <strong className="text-lg text-gray-800 block">
              {cliente.proxima_compra_estimada || "Sin cálculo"}
            </strong>
            <p className="text-sm text-gray-600 mt-1">
              Ciclo promedio: {cliente.ciclo_compra_promedio_dias || 0} días
            </p>
          </div>

          <div className="rounded-lg bg-white border border-gray-200 p-3">
            <p className="text-xs uppercase text-gray-500 mb-1 flex items-center gap-1">
              <FaBoxes /> Recomendaciones
            </p>
            <strong className="text-lg text-gray-800 block">
              {(cliente.productos_recomendados_detalle || []).length} productos
            </strong>
            <p className="text-sm text-gray-600 mt-1">
              Calculado: {cliente.prediccion_calculada_en || "Pendiente"}
            </p>
          </div>
        </div>

        <div className="mt-4">
          <p className="text-sm font-semibold text-gray-700 mb-2">Productos sugeridos</p>
          {cliente.productos_recomendados_detalle && cliente.productos_recomendados_detalle.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {cliente.productos_recomendados_detalle.map((producto) => (
                <div key={producto.id} className="rounded-lg border border-gray-200 bg-white p-3">
                  <strong className="block text-gray-800">{producto.nombre}</strong>
                  <p className="text-sm text-gray-600">
                    {producto.tipo_prenda_nombre} · {producto.tipo_oro_nombre}
                  </p>
                  <p className="text-sm text-gray-600">Peso: {formatNumber(producto.gramos, 2)} g</p>
                  <p className="text-sm text-gray-600">Stock: {producto.existencia}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500 italic">Aún no hay productos sugeridos.</p>
          )}
        </div>
      </div>

      {/* Historial de compras */}
      <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3 text-center">
        Historial de Compras
      </h3>

      {historial && historial.length > 0 ? (
        <div className="space-y-4">
          {historial.map((venta) => (
            <div key={venta.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
              {/* Encabezado de cada venta */}
              <div className="mb-3 bg-gray-800 px-4 py-2 rounded">
                <h4 className="font-semibold text-white text-lg">
                  {venta.descripcion} — {venta.fecha}
                </h4>
              </div>

              {/* Tabla de prendas */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="bg-gray-100 border-b border-gray-300">
                    <tr>
                      <th className="px-4 py-2 font-semibold text-gray-700">Prenda</th>
                      <th className="px-4 py-2 font-semibold text-gray-700">Gramos</th>
                      <th className="px-4 py-2 font-semibold text-gray-700">Cantidad</th>
                      <th className="px-4 py-2 font-semibold text-gray-700">Subtotal</th>
                    </tr>
                  </thead>
                  <tbody>
                    {venta.prendas && venta.prendas.length > 0 ? (
                      venta.prendas.map((p) => (
                        <tr key={p.id} className="border-b border-gray-200">
                          <td className="px-4 py-2 text-gray-700">{p.prenda_nombre}</td>
                          <td className="px-4 py-2 text-gray-700">{formatNumber(p.prenda_gramos, 2)} g</td>
                          <td className="px-4 py-2 text-gray-700">{p.cantidad}</td>
                          <td className="px-4 py-2 text-gray-700">${formatNumber(p.subtotal, 0)}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="4" className="px-4 py-2 text-gray-500 italic text-center">
                          Sin prendas registradas
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500 italic">Sin registros de compras.</p>
      )}
    </div>
  );
};

export default ClientDetail;
