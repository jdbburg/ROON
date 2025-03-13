<script>
    import { onMount, onDestroy } from 'svelte';
    import { EditorState } from '@codemirror/state';
    import { EditorView, keymap, lineNumbers, drawSelection, highlightActiveLine } from '@codemirror/view';
    // import { defaultKeymap } from '@codemirror/commands';
    import { python } from '@codemirror/lang-python';
    import { basicSetup } from 'codemirror';
    import { oneDark } from '@codemirror/theme-one-dark';
    import { autocompletion, completionKeymap } from '@codemirror/autocomplete';
    import { highlightSpecialChars, rectangularSelection } from '@codemirror/view';
    import { foldGutter, foldKeymap } from '@codemirror/language';
    import { defaultKeymap, history, historyKeymap } from '@codemirror/commands';
    
  
    // Props
    export let value = ''; // Initial code content
    export let onChange = () => {}; // Callback for code changes
    export let onShiftEnter = (v, immediate) => {console.log("SHIFT+ENTER")}; // New callback for Shift+Enter
    export let immediateMode = false; // Immediate mode flag, set true to clear code upon execution

    // Custom keymap for Shift+Enter
    const shiftEnterKeymap = [
    {
        key: 'Shift-Enter', // Key combination
        run: () => {
            console.log('Shift+Enter pressed');
            onShiftEnter(value); // Call the callback with current code
            if (immediateMode) value = ""; // Clear the code
            return true; // Indicate the keypress was handled
        },
        preventDefault: true // Explicitly prevent default behavior
    },
    {
        key: 'Meta-Shift-Enter', // Key combination
        run: () => {
            console.log('Meta+Shift+Enter pressed');
            onShiftEnter(value, true); // Call the callback with current code
            // value = ""; // Clear the code
            return true; // Indicate the keypress was handled
        },
        preventDefault: true // Explicitly prevent default behavior
    }
    ];

    const debugKeymap = [
    {
        any: (view, event) => {
        console.log('Key pressed:', event.key, event.shiftKey);
        return false; // Don’t consume the event, let others handle it
        }
    }
    ];

    // Custom basic setup without conflicting defaults
    const customBasicSetup = [
        lineNumbers(),
        highlightSpecialChars(),
        history(),
        foldGutter(),
        drawSelection(),
        EditorState.allowMultipleSelections.of(true),
        rectangularSelection(),
        highlightActiveLine(),
        keymap.of([
        ...shiftEnterKeymap,  // Custom Shift+Enter binding
        ...defaultKeymap,      // Base key bindings
        ...historyKeymap,      // Undo/redo bindings
        ...foldKeymap,         // Code folding bindings
        ...completionKeymap    // Autocompletion bindings
        ])
    ];


    let editorContainer;
    let editorView;
  
    // Theme (optional, you can customize or remove)
    const editorTheme = EditorView.theme({
      '&': { height: '100%' },
      '.cm-scroller': { overflow: 'auto' }
    });
  
    onMount(() => {
      // Create the editor state
      const state = EditorState.create({
        doc: value, // Initial content
        extensions: [
        //   basicSetup, // Basic setup (line numbers, etc.)
            customBasicSetup, // Custom basic setup
          lineNumbers(), // Show line numbers
          python(), // Python syntax highlighting
          autocompletion(), // Autocompletion
          keymap.of([]), // putting shiftEnterKeymap here did not work, so use the customBasicSetup
          EditorView.updateListener.of((update) => {
            if (update.docChanged) {
              value = update.state.doc.toString(); // Update reactive value
              onChange(value); // Notify parent of changes
            }
          }),
        //   editorTheme
        oneDark,
        
        ]
      });
  
      // Initialize the editor view
      editorView = new EditorView({
        state,
        parent: editorContainer
      });
  
      return () => {
        editorView.destroy(); // Clean up on unmount
      };
    });
  
    // Update editor content if `value` changes externally
    $: if (editorView && value !== editorView.state.doc.toString()) {
      editorView.dispatch({
        changes: { from: 0, to: editorView.state.doc.length, insert: value }
      });
    }
  </script>
  
  <div bind:this={editorContainer} class="editor-container"></div>
  
  <style>
    .editor-container {
        position: relative;
        /* bottom: 200px; */
      width: 100%;
      /* height: 800px; Adjust height as needed */
      border: 1px solid #ccc;
      z-index: 9999;
    }
  </style>