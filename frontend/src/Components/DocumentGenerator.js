import { Button, Col, Form, Input, Row } from 'antd';
import Docxtemplater from 'docxtemplater';
import ImageModule from 'docxtemplater-image-module-free';
import { saveAs } from 'file-saver';
import PizZip from 'pizzip';
import React, { useEffect, useState } from 'react';

const { TextArea } = Input;

const DocumentGenerator = () => {
  const [formValues, setFormValues] = useState({
    product: '',
    destination_country: '',
    product_description: '',
    destination_country_profile: '',
    trade_dependence_index: '',
    export_concentration_index: '',
    trade_complementary_index: '',
    regulation_quality_policy: '',
    tariff_logistic: '',
    market_competitiveness: '',
    trade_representative: '',
    strategy: '',
    trend_chart: ''
  });
  const [form] = Form.useForm();

  useEffect(() => {
    form.setFieldsValue(formValues);
  }, [formValues, form]);

  // const getImageOptions = () => ({
  //   getImage: (tagValue) => base64ImageToArrayBuffer(tagValue),
  //   getSize: () => [150, 150], // Ukuran gambar dalam piksel [width, height]
  // });
  const getImageOptions = () => ({
    getImage: (tagValue) => {
        if (tagValue.startsWith('data:image')) {
            const base64Data = tagValue.split(',')[1];
            const binaryString = atob(base64Data); // Decode Base64 string
            const len = binaryString.length;
            const arrayBuffer = new Uint8Array(len);
            for (let i = 0; i < len; i++) {
                arrayBuffer[i] = binaryString.charCodeAt(i);
            }
            return arrayBuffer.buffer; // Return ArrayBuffer
        }
        return fetch(tagValue).then((res) => res.arrayBuffer()); // Handle URLs
    },
    getSize: () => [300, 200], // Set width and height
});


  const onFinish = async (values) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_API}/generate-market-inteligence`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify({
            product: values.product,
            destination_country: values.destination_country,
          }),
        }
      );

      const data = await response.json();
      if (response.status === 200) {
        console.log(data)
        setFormValues({
          ...formValues,
          product: values.product,
          destination_country: values.destination_country,
          product_description: data.data.product_description + '\n\n' + data.data.export_trend,
          destination_country_profile: data.data.destination_country_profile,
          trade_dependence_index: data.data.trade_dependence_index,
          export_concentration_index: data.data.export_concentration_index,
          trade_complementary_index: data.data.trade_complementary_index,
          regulation_quality_policy: data.data.regulation_quality_policy,
          tariff_logistic: data.data.tariff_logistic,
          market_competitiveness: data.data.market_competitiveness,
          trade_representative: data.data.trade_representative,
          strategy: data.data.strategy,
          trend_chart: data.data.attachment_export_trend
          ,
        });
        alert('Content generated successfully!');
      } else {
        alert('Failed to generate content.');
      }
    } catch (error) {
      console.error('Error fetching API:', error);
      alert('Something went wrong, please try again later.');
    }
  };

  const generateDocx = async () => {
    try {
      console.log(form)
      const templatePath = '/MARKET MIND.docx';
      const content = await fetch(templatePath).then((response) =>
        response.arrayBuffer()
      );
      const zip = new PizZip(content);
      console.log(getImageOptions())
      const imageModule = new ImageModule(getImageOptions());
      console.log(imageModule)
      const doc = new Docxtemplater(zip, {
        modules: [imageModule], // Attach the ImageModule
    });
    

      doc.setData(formValues);
      console.log(doc)
      doc.render();

      const blob = doc.getZip().generate({ type: 'blob' });
      saveAs(blob, 'MarketIntelligenceReport.docx');
    } catch (error) {
      console.error('Error generating DOCX:', error);
      console.log(error)
      alert('Failed to generate the document. Please try again.');
    }
  };

  return (
    <Row gutter={16} style={{ padding: '1rem' }}>
      {/* Left side - Form */}
      <Col span={5}>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item
            label="Negara Tujuan Ekspor"
            name="destination_country"
            rules={[{ required: true, message: 'Negara tujuan diperlukan.' }]}
          >
            <Input placeholder="India" />
          </Form.Item>

          <Form.Item
            label="Produk"
            name="product"
            rules={[{ required: true, message: 'Produk diperlukan.' }]}
          >
            <Input placeholder="Kopi" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              Generate
            </Button>
          </Form.Item>
        </Form>
      </Col>

      {/* Right side - Form for Rich Data */}
      <Col span={18}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '1rem',
          }}
        >
          <Button
            type="primary"
            style={{ backgroundColor: 'green' }}
            onClick={generateDocx}
            // disabled={!formValues.product_description || !formValues.destination_country_profile}
          >
            Export To Word
          </Button>
        </div>

        <Form layout="vertical" form={form}>
          <Form.Item label="Profil Negara" name="destination_country_profile">
            <TextArea rows={4} placeholder="Masukan profil negara ..." readOnly />
          </Form.Item>
          <Form.Item label="Deskripsi Produk" name="product_description">
            <TextArea rows={4} placeholder="Masukan deskripsi produk ..." readOnly />
          </Form.Item>
          <Form.Item label="Trend Ekspor" name="trend_chart">
            <div style={{ textAlign: 'center' }}>
              <img
                src={formValues.trend_chart}
                alt="Trend Preview"
                style={{ maxWidth: '100%', maxHeight: '150px' }}
              />
            </div>
          </Form.Item>
          <Form.Item label="Peran Perdagangan Internasional" name="trade_dependence_index">
            <TextArea rows={4} placeholder="Masukan peran perdagangan internasional ..." readOnly />
          </Form.Item>
          <Form.Item label="Arah Perdagangan" name="export_concentration_index">
            <TextArea rows={4} placeholder="Masukan arah perdagangan ..." readOnly />
          </Form.Item>
          <Form.Item label="Struktur Perdagangan" name="trade_complementary_index">
            <TextArea rows={4} placeholder="Masukan struktur perdagangan ..." readOnly />
          </Form.Item>
          <Form.Item label="Regulasi dan Syarat Mutu" name="regulation_quality_policy">
            <TextArea rows={4} placeholder="Masukan regulasi dan syarat mutu ..." readOnly />
          </Form.Item>
          <Form.Item label="Logistik" name="tariff_logistic">
            <TextArea rows={4} placeholder="Masukan informasi logistik ..." readOnly />
          </Form.Item>
          <Form.Item label="Analisis Daya Saing" name="market_competitiveness">
            <TextArea rows={4} placeholder="Masukan analisis daya saing ..." readOnly />
          </Form.Item>
          <Form.Item label="Perwakilan Perdagangan" name="trade_representative">
            <TextArea rows={4} placeholder="Masukan daftar perwakilan perdagangan ..." readOnly />
          </Form.Item>
          <Form.Item label="Strategi dan Rekomendasi" name="strategy">
            <TextArea rows={4} placeholder="Masukan strategi dan rekomendasi ..." readOnly />
          </Form.Item>
        </Form>
      </Col>
    </Row>
  );
};

export default DocumentGenerator;
