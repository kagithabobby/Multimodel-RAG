import React, { useEffect, useRef } from 'react';
import * as pdfjsLib from 'pdfjs-dist/build/pdf';
import 'pdfjs-dist/build/pdf.worker.entry';

const PDFViewer = ({ pdfUrl, currentPage, highlightBbox }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!pdfUrl) return;

    const renderPage = async () => {
      try {
        const loadingTask = pdfjsLib.getDocument(pdfUrl);
        const pdf = await loadingTask.promise;
        
        // Ensure page is within bounds
        const pageNum = Math.min(Math.max(1, currentPage), pdf.numPages);
        const page = await pdf.getPage(pageNum);

        const scale = 1.5;
        const viewport = page.getViewport({ scale });

        const canvas = canvasRef.current;
        if (!canvas) return;
        
        const context = canvas.getContext('2d');
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
          canvasContext: context,
          viewport: viewport
        };
        await page.render(renderContext).promise;

        // Draw highlight if provided
        if (highlightBbox && highlightBbox.length === 4) {
          context.beginPath();
          // bbox format usually [x0, y0, x1, y1]
          const [x0, y0, x1, y1] = highlightBbox;
          // Scale coordinates
          const scaledX = x0 * scale;
          const scaledY = y0 * scale;
          const scaledW = (x1 - x0) * scale;
          const scaledH = (y1 - y0) * scale;
          
          context.rect(scaledX, scaledY, scaledW, scaledH);
          context.lineWidth = 3;
          context.strokeStyle = 'rgba(255, 0, 0, 0.8)';
          context.stroke();
          context.fillStyle = 'rgba(255, 255, 0, 0.3)';
          context.fill();
        }

      } catch (err) {
        console.error("Error rendering PDF:", err);
      }
    };

    renderPage();
  }, [pdfUrl, currentPage, highlightBbox]);

  if (!pdfUrl) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-100 text-gray-500 rounded-lg">
        <p>No document uploaded</p>
      </div>
    );
  }

  return (
    <div className="overflow-auto bg-gray-200 p-4 flex justify-center h-full">
      <canvas ref={canvasRef} className="shadow-lg bg-white rounded-sm"></canvas>
    </div>
  );
};

export default PDFViewer;
