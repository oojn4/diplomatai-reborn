import Docxtemplater from 'docxtemplater';
import { saveAs } from 'file-saver';
import * as html2pdf from 'html2pdf.js';
import PizZip from 'pizzip';
import React, { useState } from 'react';

const InvoiceForm = () => {
  const [templates, setTemplates] = useState([
    { name: 'MARKET MIND', fields: ['product', 'destination_country'], path: '/MARKET MIND.docx' },
    { name: 'Template 2', fields: ['FirstName', 'LastName', 'Email', 'Address', 'PhoneNumber'], path: '/t2.docx' },
    { name: 'Template 3', fields: ['Company', 'Position', 'StartDate', 'EndDate', 'Responsibilities', 'Achievements', 'References'], path: '/t3.docx' },
  ]);
  const [template, setTemplate] = useState(null);
  const [values, setValues] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleTemplateChange = (event) => {
    const selectedTemplate = templates.find(t => t.name === event.target.value);
    setTemplate(selectedTemplate);
    setValues({});
  };

  const handleInputChange = (event) => {
    setValues({ ...values, [event.target.name]: event.target.value });
  };

  const validateInputs = () => {
    return template.fields.every(field => values[field]);
  };

  const handleDocxDownload = async () => {
    if (!template) return;
    if (!validateInputs()) {
      alert('Please fill out all fields!');
      return;
    }

    try {
      setIsLoading(true);
      const content = await fetch(template.path).then(response => response.arrayBuffer());
      const zip = new PizZip(content);
      console.log("gagal zip")
      const doc = new Docxtemplater(zip);
      console.log("gagal Docxtemplater")
      doc.setData(values);
      console.log(doc)
      console.log(templates)
      doc.render();
      const blob = doc.getZip().generate({ type: 'blob' });
      saveAs(blob, 'output.docx');
    } catch (error) {
      console.error('Error generating DOCX:', error);
      alert('Failed to generate the document. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePdfDownload = async () => {
    if (!template) return;
    if (!validateInputs()) {
      alert('Please fill out all fields!');
      return;
    }

    try {
      setIsLoading(true);
      const content = await fetch(template.path).then(response => response.arrayBuffer());
      
      console.log(content)
      const zip = new PizZip(content);
      console.log("gagal Docxtemplater")
      const doc = new Docxtemplater(zip);
      doc.setData(values);
      console.log(values)
      console.log(templates)
      doc.render();
      const outputHtml = doc.getZip().generate({ type: 'string' });

      // Convert HTML to PDF
      const element = document.createElement('div');
      element.innerHTML = outputHtml;
      const pdfOptions = {
        filename: 'output.pdf',
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      };
      html2pdf().from(element).set(pdfOptions).save();
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate the PDF. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1>Invoice Form</h1>
      <select onChange={handleTemplateChange} defaultValue="">
        <option value="" disabled>Select a template</option>
        {templates.map(t => <option key={t.name} value={t.name}>{t.name}</option>)}
      </select>
      {template && template.fields.map(field => (
        <input
          key={field}
          type="text"
          name={field}
          value={values[field]}
          onChange={handleInputChange}
          placeholder={field}
        />
      ))}
      {template && (
        <>
          <button onClick={handleDocxDownload} disabled={isLoading}>
            {isLoading ? 'Generating DOCX...' : 'Download DOCX'}
          </button>
          {/* <button onClick={handlePdfDownload} disabled={isLoading}>
            {isLoading ? 'Generating PDF...' : 'Download PDF'}
          </button> */}
        </>
      )}
    </div>
  );
};

export default InvoiceForm;
