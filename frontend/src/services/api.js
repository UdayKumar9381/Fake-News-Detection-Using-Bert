import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export const predictText = (text) =>
  axios.post(`${API_BASE_URL}/predict-text`, { text });

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return axios.post(`${API_BASE_URL}/upload-file`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const verifySource = (text) =>
  axios.post(`${API_BASE_URL}/verify-source`, { text });

export const getModelInfo = () =>
  axios.get(`${API_BASE_URL}/model-info`);
