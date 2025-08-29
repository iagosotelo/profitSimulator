import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";

export default function App() {
  const [cuantificaciones, setCuantificaciones] = useState(1);
  const [beneficioDiario, setBeneficioDiario] = useState(1); // %
  const [saldoInicial, setSaldoInicial] = useState(500);
  const [saldoRetiro, setSaldoRetiro] = useState(500);
  const [importeRetiro, setImporteRetiro] = useState(100);

  const [referidos, setReferidos] = useState([]);
  const [nuevoSaldoRef, setNuevoSaldoRef] = useState(0);
  const [nuevoNivelRef, setNuevoNivelRef] = useState("A");

  // Porcentajes de ganancia de referidos según nivel
  const porcentajesRef = { A: 0.05, B: 0.03, C: 0.01 };

  const addReferido = () => {
    if (nuevoSaldoRef > 0) {
      setReferidos([...referidos, { saldo: Number(nuevoSaldoRef), nivel: nuevoNivelRef }]);
      setNuevoSaldoRef(0);
    }
  };

  const simular = () => {
    let saldo = saldoInicial;
    let resultadosDiarios = [];
    let resultadosMensuales = [];
    let gananciaTotal = 0;

    // Copia de saldos de referidos
    let referidosSim = referidos.map(r => ({ ...r }));

    for (let dia = 1; dia <= 360; dia++) {
      // Ganancia propia con cuantificaciones
      let gananciaPropia = 0;
      let saldoTemp = saldo;
      for (let c = 0; c < cuantificaciones; c++) {
        let g = saldoTemp * (beneficioDiario / 100 / cuantificaciones);
        saldoTemp += g;
        gananciaPropia += g;
      }
      saldo = saldoTemp;

      // Ganancia referidos
      let gananciaReferidos = 0;
      referidosSim = referidosSim.map(r => {
        let gRef = 0;
        let saldoTempRef = r.saldo;
        for (let c = 0; c < cuantificaciones; c++) {
          let g = saldoTempRef * (beneficioDiario / 100 / cuantificaciones);
          saldoTempRef += g;
          gRef += g;
        }
        let gComision = gRef * (porcentajesRef[r.nivel] || 0);
        gananciaReferidos += gComision;
        return { ...r, saldo: saldoTempRef };
      });

      let gananciaDia = gananciaPropia + gananciaReferidos;
      gananciaTotal += gananciaDia;

      // Retirada si aplica
      if (saldo >= saldoRetiro) {
        saldo -= importeRetiro;
      }

      // Guardar en resultados diarios (solo 90 días)
      if (dia <= 90) {
        resultadosDiarios.push({
          dia,
          saldo: saldo.toFixed(2),
          gananciaPropia: gananciaPropia.toFixed(2),
          gananciaReferidos: gananciaReferidos.toFixed(2),
          gananciaTotal: gananciaTotal.toFixed(2),
        });
      }

      // Guardar resumen mensual cada 30 días
      if (dia % 30 === 0) {
        resultadosMensuales.push({
          mes: dia / 30,
          saldo: saldo.toFixed(2),
          gananciaTotal: gananciaTotal.toFixed(2),
        });
      }
    }

    return { resultadosDiarios, resultadosMensuales };
  };

  const { resultadosDiarios, resultadosMensuales } = simular();

  return (
    <div className="p-6 grid gap-6">
      <h1 className="text-2xl font-bold">Simulador de Inversión (USDT)</h1>

      {/* Configuración principal */}
      <Card>
        <CardContent className="grid gap-4 p-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label>Nº de cuantificaciones diarias</label>
              <Input type="number" value={cuantificaciones} onChange={e => setCuantificaciones(+e.target.value)} />
            </div>
            <div>
              <label>Beneficio propio diario (%)</label>
              <Input type="number" value={beneficioDiario} onChange={e => setBeneficioDiario(+e.target.value)} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Configuración de retiradas */}
      <Card>
        <CardContent className="grid gap-4 p-4">
          <h2 className="text-lg font-semibold">Configuración de retiradas</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label>Saldo a partir de retirada (USDT)</label>
              <Input type="number" value={saldoRetiro} onChange={e => setSaldoRetiro(+e.target.value)} />
            </div>
            <div>
              <label>Importe a retirar (USDT)</label>
              <Input type="number" value={importeRetiro} onChange={e => setImporteRetiro(+e.target.value)} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Referidos */}
      <Card>
        <CardContent className="grid gap-4 p-4">
          <h2 className="text-lg font-semibold">Gestión de referidos</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label>Saldo referido (USDT)</label>
              <Input type="number" value={nuevoSaldoRef} onChange={e => setNuevoSaldoRef(e.target.value)} />
            </div>
            <div>
              <label>Nivel</label>
              <Select value={nuevoNivelRef} onChange={e => setNuevoNivelRef(e.target.value)}>
                <option value="A">Nivel A</option>
                <option value="B">Nivel B</option>
                <option value="C">Nivel C</option>
              </Select>
            </div>
            <div className="flex items-end">
              <Button onClick={addReferido}>Añadir referido</Button>
            </div>
          </div>

          <ul className="list-disc ml-6">
            {referidos.map((r, i) => (
              <li key={i}>Nivel {r.nivel} - Saldo: {r.saldo} USDT</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Tabla diaria */}
      <Card>
        <CardContent className="p-4">
          <h2 className="text-lg font-semibold">Ganancias diarias (90 días)</h2>
          <table className="table-auto w-full text-sm">
            <thead>
              <tr>
                <th>Día</th>
                <th>Saldo</th>
                <th>Ganancia propia</th>
                <th>Ganancia referidos</th>
                <th>Ganancia total</th>
              </tr>
            </thead>
            <tbody>
              {resultadosDiarios.map((r) => (
                <tr key={r.dia}>
                  <td>{r.dia}</td>
                  <td>{r.saldo}</td>
                  <td>{r.gananciaPropia}</td>
                  <td>{r.gananciaReferidos}</td>
                  <td>{r.gananciaTotal}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      {/* Tabla mensual */}
      <Card>
        <CardContent className="p-4">
          <h2 className="text-lg font-semibold">Ganancias mensuales (12 meses)</h2>
          <table className="table-auto w-full text-sm">
            <thead>
              <tr>
                <th>Mes</th>
                <th>Saldo</th>
                <th>Ganancia total acumulada</th>
              </tr>
            </thead>
            <tbody>
              {resultadosMensuales.map((r) => (
                <tr key={r.mes}>
                  <td>{r.mes}</td>
                  <td>{r.saldo}</td>
                  <td>{r.gananciaTotal}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
