
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AdminLayout from './layoutsAdmin/AdminLayout';
import Login from "./Pages/Login";
import Inicio from './Pages/Inicio';
import Clientes from './Pages/Clientes';
import Proveedores from './Pages/Proveedores';
import CompraForm from './Pages/CompraForm';
import Venta from './Pages/Venta';
import './App.css';


function App() {
  return (
    <Router>
      <Routes>
        {/* 🔹 Ruta principal redirige al login */}
        <Route path="/" element={<Login />} />

        {/* 🔹 Rutas protegidas del panel admin */}
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<Inicio />} />
          <Route path="clientes" element={<Clientes />} />
          <Route path="proveedores" element={<Proveedores />} />
          <Route path="compras" element={<CompraForm />} />
          <Route path="ventas" element={<Venta />} />
        </Route>

        {/* 🔹 Si la ruta no existe, redirigir al login */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;