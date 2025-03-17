# エージェント対話履歴セクション
st.subheader("エージェント対話履歴")
dialog_container = st.container()

# 実行ボタンが押された場合の処理
if run_button:
    if not user_input:
        st.error("文章が入力されていません。")
    elif st.session_state.processing:
        st.warning("すでに処理中です。完了までお待ちください。")
    else:
        st.session_state.processing = True
        graph = create_workflow_graph()
        client = get_client()
        
        # 対話履歴の初期化
        st.session_state.current_dialog_history = []
        
        # 初期状態の作成と対話履歴への追加
        initial_state = create_initial_state(user_input)
        initial_state = add_to_dialog_history(
            initial_state,
            "system",
            "新しいテキストが入力されました。ワークフローを開始します。"
        )
        st.session_state.current_dialog_history = initial_state["dialog_history"]
        
        # セッション状態に最終結果用の初期状態をセット
        st.session_state.final_state = initial_state.copy()
        
        # 対話履歴の表示（処理開始メッセージ）
        with dialog_container:
            st.info("処理を開始しました。完了するまでしばらくお待ちください...")
        
        # ワークフロー処理をバックグラウンドスレッドで実行
        def run_workflow():
            try:
                result = graph.invoke(initial_state)
                st.session_state.final_state.update(result)
                # 対話履歴も更新
                if "dialog_history" in result:
                    st.session_state.current_dialog_history = result["dialog_history"]
            except Exception as e:
                st.session_state.error_message = f"処理中にエラーが発生しました: {str(e)}"
            finally:
                st.session_state.processing = False
                st.session_state.reset_processing = True
                st.rerun()
        
        threading.Thread(target=run_workflow, daemon=True).start()

# 処理中の表示
if st.session_state.processing:
    with dialog_container:
        st.warning("処理中です。完了までお待ちください...")
        st.spinner("実行中...")
# 処理中でなければ対話履歴を表示
elif st.session_state.current_dialog_history:
    with dialog_container:
        display_dialog_history(st.session_state.current_dialog_history)
