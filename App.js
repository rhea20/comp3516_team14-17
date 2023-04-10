import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, Button, CheckBox, TouchableOpacity } from 'react-native';
import QRCode from 'qrcode';
import DocumentPicker from 'react-native-document-picker';

export default function App() {

    return (
    <View>
      <TextInput
        value={chunks}
        onChangeText={setChunks}
        placeholder="Chunk size (bytes)"
      />
      <TextInput
        value={interval}
        onChangeText={setInterval}
        placeholder="Extra interval (ms)"
      />
      <TouchableOpacity onPress={loadFile}>
        <Text>Select File</Text>
      </TouchableOpacity>
      <Button title="Stop" onPress={stop} />
      <Button title="Start" onPress={start} />
      <Text>{progress}</Text>
      <Text>{placeHolder}</Text>
    </View>
  );

  const [chunks, setChunks] = useState('2000');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [stopLoop, setStopLoop] = useState(false);
  const [maxWidth, setMaxWidth] = useState(0);
  const [maxHeight, setMaxHeight] = useState(0);
  const [fileName, setFileName] = useState('');
  const [fileType, setFileType] = useState('');
  const [interval, setInterval] = useState('200');
  const [progress, setProgress] = useState('');
  const [placeHolder, setPlaceHolder] = useState('');

  const loadFile = async () => {
    const result = await DocumentPicker.getDocumentAsync({});
    if (result.type === 'success') {
      const { uri } = result;
      const response = await fetch(uri);
      const buffer = await response.arrayBuffer();
      setStopLoop(true);
      setCurrentIndex(0);
      setMaxWidth(0);
      setMaxHeight(0);
      loadArrayBufferToChunks(buffer, result.name, result.type);
      setStopLoop(false);
      showAnimatedQRCode();
    }
  };

  const loadArrayBufferToChunks = (bytes, filename, type) => {
    const data = concatTypedArrays(stringToBytes(encodeURIComponent(`${filename}|${type}|`)), new Uint8Array(bytes));
    const chunkSize = parseInt(chunkSize);
    const num = Math.ceil(data.length / chunkSize);
    const chunks = [];
    for (let i = 0; i < num; i++) {
      const start = i * chunkSize;
      let chunk = data.slice(start, start + chunkSize);
      const meta = `${i + 1}/${num}|`;
      chunk = concatTypedArrays(stringToBytes(meta), chunk);
      chunks.push(chunk);
    }
    setChunks(chunks);
  };

  const showAnimatedQRCode = () => {
    createQRCode(chunks[currentIndex]);
    setCurrentIndex((prevIndex) => prevIndex + 1);
    if (currentIndex === chunks.length) {
      setCurrentIndex(0);
      if (!loopChk) {
        return;
      }
    }
    if (stopLoop) {
      setStopLoop(false);
      return;
    }
    const interval = parseInt(intervalTime);
    setTimeout(showAnimatedQRCode, interval);
  };

  const createQRCode = (data) => {
    const typeNumber = 0;
    const errorCorrectionLevel = 'L';
    const qr = QRCode.create(data, { typeNumber, errorCorrectionLevel });
    const svg = qr.svg();
    const img = svgToImg(svg);
    const width = parseInt(img.getAttribute('width').replace('px', ''));
    const height = parseInt(img.getAttribute('height').replace('px', ''));
    setMaxWidth((prevWidth) => Math.max(prevWidth, width));
    setMaxHeight((prevHeight) => Math.max(prevHeight, height));
  };

  const svgToImg = (svg) => {
    const wrapper = document.createElement('div');
    wrapper.innerHTML = svg;
    return wrapper.firstChild;
  };

  //https://stackoverflow.com/questions/33702838/how-to-append-bytes-multi-bytes-and-buffer-to-arraybuffer-in-javascript
  const concatTypedArrays = (a, b) => {
    const newLength = a.length + b.byteLength;
    const c = new Uint8Array(newLength);
    c.set(a, 0);
    c.set(b, a.length);
    return c;
  };

  const stringToBytes = (s) => {
  const bytes = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) {
    const c = s.charCodeAt(i);
    bytes[i] = c & 0xff;
  }
  return bytes;
};
  const stop = () => {
    setStopLoop(true);
  };

  const start = () => {
    showAnimatedQRCode();
  };

}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});