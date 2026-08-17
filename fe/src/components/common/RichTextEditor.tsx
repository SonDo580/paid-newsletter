import Image from "@tiptap/extension-image";
import Placeholder from "@tiptap/extension-placeholder";
import {
  Editor,
  EditorContent,
  useEditor,
  useEditorState,
} from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import {
  Bold as BoldIcon,
  Heading2 as Heading2Icon,
  Image as ImageIcon,
  Italic as ItalicIcon,
} from "lucide-react";
import { useState, type ChangeEvent, type ReactNode } from "react";
import { toast } from "sonner";
import { cn } from "~/lib/utils";
import { Spinner } from "../ui/spinner";

interface ToolbarButtonProps {
  onClick: () => void;
  isActive?: boolean;
  disabled?: boolean;
  children: ReactNode;
}

function ToolbarButton({
  onClick,
  isActive,
  disabled,
  children,
}: ToolbarButtonProps) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={cn(
        "cursor-pointer px-2 py-1 rounded hover:bg-background disabled:opacity-50 disabled:cursor-not-allowed",
        isActive ? "bg-background text-blue-600 font-bold" : "",
      )}
    >
      {children}
    </button>
  );
}

interface EditorToolbarProps {
  editor: Editor;
  onImageSelect: (e: ChangeEvent<HTMLInputElement>) => void;
  isUploading: boolean;
}

function EditorToolbar({
  editor,
  onImageSelect,
  isUploading,
}: EditorToolbarProps) {
  const iconCls = "w-4 h-4";

  const editorState = useEditorState({
    editor,
    selector: (ctx) => ({
      isBold: ctx.editor.isActive("bold"),
      isItalic: ctx.editor.isActive("italic"),
      isHeading2: ctx.editor.isActive("heading", { level: 2 }),
    }),
  });

  return (
    <div className="flex items-center gap-1 p-1 border border-b-0 rounded-t-md bg-muted/50 text-xs">
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleBold().run()}
        isActive={editorState?.isBold}
      >
        <BoldIcon className={iconCls} />
      </ToolbarButton>

      <ToolbarButton
        onClick={() => editor.chain().focus().toggleItalic().run()}
        isActive={editorState?.isItalic}
      >
        <ItalicIcon className={iconCls} />
      </ToolbarButton>

      <ToolbarButton
        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        isActive={editorState?.isHeading2}
      >
        <Heading2Icon className={iconCls} />
      </ToolbarButton>

      <label
        className={cn(
          "px-2 py-1 rounded cursor-pointer hover:bg-background",
          isUploading ? "opacity-50 pointer-events-none" : "",
        )}
      >
        {isUploading ? <Spinner /> : <ImageIcon className={iconCls} />}
        <input
          type="file"
          accept="image/*"
          disabled={isUploading}
          className="hidden"
          onChange={onImageSelect}
        />
      </label>
    </div>
  );
}

interface RichTextEditorProps {
  value: string;
  placeholder: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  uploadImageApi: (file: File) => Promise<string>; // return image URL
}

export function RichTextEditor({
  value,
  placeholder = "",
  onChange,
  onBlur,
  uploadImageApi,
}: RichTextEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Image.configure({
        inline: true,
        allowBase64: false,
      }),
      Placeholder.configure({
        placeholder,
      }),
    ],
    content: value,
    editorProps: {
      attributes: {
        class:
          "prose max-w-none min-h-[250px] p-3 border border-t-0 rounded-b-md focus:outline-none",
      },
    },
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
    onBlur: () => {
      onBlur?.();
    },
  });

  const [isUploading, setIsUploading] = useState(false);

  const handleImageUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) {
      return;
    }

    try {
      setIsUploading(true);
      const imageUrl = await uploadImageApi(file);
      editor.chain().focus().setImage({ src: imageUrl }).run();
    } catch (err) {
      console.error("Failed to upload image:", err);
      toast.error("Failed to upload image. Please try again.");
    } finally {
      setIsUploading(false);
      // Clear file input value so user can upload the file again
      e.target.value = "";
    }
  };

  if (!editor) {
    return null;
  }
  return (
    <div className="flex flex-col">
      <EditorToolbar
        editor={editor}
        onImageSelect={handleImageUpload}
        isUploading={isUploading}
      />
      <EditorContent editor={editor} />
    </div>
  );
}
