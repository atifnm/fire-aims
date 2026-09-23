import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ScanLine, Keyboard } from 'lucide-react'
import { Html5Qrcode } from 'html5-qrcode'
import Layout from '../components/Layout'
import api from '../api/client'

export default function Scan() {
  const navigate = useNavigate()
  const scannerRef = useRef(null)
  const [scanning, setScanning] = useState(false)
  const [manualCode, setManualCode] = useState('')
  const [error, setError] = useState('')
  const [cameraError, setCameraError] = useState('')

  useEffect(() => {
    return () => {
      if (scannerRef.current) {
        scannerRef.current.stop().catch(() => {})
      }
    }
  }, [])

  const resolveAndGo = async (rawValue) => {
    // QR payload is "fireaims://scan/FE-00001" - extract the trailing asset code.
    // Barcodes and manual entry are the plain asset code itself.
    const code = rawValue.includes('/') ? rawValue.split('/').pop() : rawValue.trim()
    try {
      const res = await api.get(`/assets/scan/${code}`)
      navigate(`/assets/${res.data.asset_id}`)
    } catch (err) {
      setError(`No equipment found for code "${code}".`)
    }
  }

  const startScanning = async () => {
    setError('')
    setCameraError('')
    setScanning(true)
    try {
      const html5Qr = new Html5Qrcode('qr-reader')
      scannerRef.current = html5Qr
      await html5Qr.start(
        { facingMode: 'environment' },
        { fps: 10, qrbox: { width: 240, height: 240 } },
        async (decodedText) => {
          await html5Qr.stop()
          setScanning(false)
          resolveAndGo(decodedText)
        },
        () => {} // ignore per-frame scan failures
      )
    } catch (err) {
      setCameraError('Could not access camera. You can still enter the code manually below.')
      setScanning(false)
    }
  }

  const stopScanning = async () => {
    if (scannerRef.current) {
      await scannerRef.current.stop().catch(() => {})
    }
    setScanning(false)
  }

  return (
    <Layout>
      <div className="p-4 md:p-8 max-w-md mx-auto">
        <h1 className="text-2xl font-bold text-fire-800 mb-1 flex items-center gap-2">
          <ScanLine /> Scan Equipment
        </h1>
        <p className="text-slate-500 text-sm mb-6">Scan a QR code or barcode on any fire safety asset.</p>

        <div className="bg-white rounded-xl shadow p-4 mb-4">
          <div id="qr-reader" className="w-full rounded-lg overflow-hidden bg-slate-900" style={{ minHeight: scanning ? 260 : 0 }} />
          {!scanning ? (
            <button onClick={startScanning} className="w-full mt-3 bg-fire-700 hover:bg-fire-800 text-white font-semibold py-3 rounded-lg">
              Start Camera Scan
            </button>
          ) : (
            <button onClick={stopScanning} className="w-full mt-3 border font-semibold py-3 rounded-lg text-slate-600">
              Stop Scanning
            </button>
          )}
          {cameraError && <div className="text-sm text-orange-600 mt-2">{cameraError}</div>}
        </div>

        <div className="bg-white rounded-xl shadow p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
            <Keyboard size={16} /> Enter Code Manually
          </div>
          <form
            onSubmit={(e) => { e.preventDefault(); if (manualCode.trim()) resolveAndGo(manualCode.trim()) }}
            className="flex gap-2"
          >
            <input
              value={manualCode} onChange={(e) => setManualCode(e.target.value)}
              placeholder="e.g. FE-00001"
              className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-fire-500"
            />
            <button type="submit" className="bg-fire-700 hover:bg-fire-800 text-white px-4 py-2 rounded-lg text-sm font-semibold">Go</button>
          </form>
          {error && <div className="text-sm text-red-600 mt-2">{error}</div>}
        </div>
      </div>
    </Layout>
  )
}
