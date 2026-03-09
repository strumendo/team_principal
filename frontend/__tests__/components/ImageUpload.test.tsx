/**
 * ImageUpload component tests.
 * Testes do componente ImageUpload.
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ImageUpload from "@/components/ImageUpload";

const originalFetch = global.fetch;

beforeEach(() => {
  global.fetch = jest.fn();
  global.URL.createObjectURL = jest.fn(() => "blob:http://localhost/test-preview");
});

afterEach(() => {
  global.fetch = originalFetch;
});

const defaultProps = {
  currentImageUrl: null,
  uploadUrl: "/uploads/users/1/avatar",
  token: "test-token",
  onUploadSuccess: jest.fn(),
  label: "Avatar",
};

function getFileInput(): HTMLInputElement {
  return document.querySelector('input[type="file"]') as HTMLInputElement;
}

describe("ImageUpload / Upload de Imagem", () => {
  it("renders label and upload button / renderiza label e botao de upload", () => {
    render(<ImageUpload {...defaultProps} />);
    expect(screen.getByText("Avatar")).toBeInTheDocument();
    expect(screen.getByText("Upload")).toBeInTheDocument();
  });

  it("shows current image when provided / exibe imagem atual quando fornecida", () => {
    render(<ImageUpload {...defaultProps} currentImageUrl="/uploads/avatar.jpg" />);
    const img = screen.getByAltText("Avatar");
    expect(img).toBeInTheDocument();
  });

  it("validates file type / valida tipo de arquivo", () => {
    render(<ImageUpload {...defaultProps} />);
    const input = getFileInput();
    const file = new File(["test"], "test.pdf", { type: "application/pdf" });
    fireEvent.change(input, { target: { files: [file] } });
    expect(screen.getByText(/Invalid file type/)).toBeInTheDocument();
  });

  it("validates file size / valida tamanho do arquivo", () => {
    render(<ImageUpload {...defaultProps} />);
    const input = getFileInput();
    const largeContent = new ArrayBuffer(6 * 1024 * 1024);
    const file = new File([largeContent], "large.jpg", { type: "image/jpeg" });
    fireEvent.change(input, { target: { files: [file] } });
    expect(screen.getByText(/File too large/)).toBeInTheDocument();
  });

  it("shows preview after valid file selection / exibe preview apos selecao valida", () => {
    render(<ImageUpload {...defaultProps} />);
    const input = getFileInput();
    const file = new File(["test"], "photo.jpg", { type: "image/jpeg" });
    fireEvent.change(input, { target: { files: [file] } });
    expect(global.URL.createObjectURL).toHaveBeenCalledWith(file);
  });

  it("calls upload endpoint on submit / chama endpoint de upload ao submeter", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ url: "/uploads/avatar-new.jpg" }),
    });

    const onSuccess = jest.fn();
    render(<ImageUpload {...defaultProps} onUploadSuccess={onSuccess} />);

    const input = getFileInput();
    const file = new File(["test"], "photo.jpg", { type: "image/jpeg" });
    fireEvent.change(input, { target: { files: [file] } });

    fireEvent.click(screen.getByText("Upload"));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
      expect(onSuccess).toHaveBeenCalledWith("/uploads/avatar-new.jpg");
    });
  });

  it("shows error on upload failure / exibe erro em falha de upload", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ detail: "Upload failed" }),
    });

    render(<ImageUpload {...defaultProps} />);
    const input = getFileInput();
    const file = new File(["test"], "photo.jpg", { type: "image/jpeg" });
    fireEvent.change(input, { target: { files: [file] } });
    fireEvent.click(screen.getByText("Upload"));

    await waitFor(() => {
      expect(screen.getByText("Upload failed")).toBeInTheDocument();
    });
  });
});
