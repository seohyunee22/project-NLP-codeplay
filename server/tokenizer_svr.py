from miditok import MMM, TokenizerConfig
from typing import Union, Optional
from pathlib import Path

class CodeplayTokenizer(MMM):
    def __init__(self, config: TokenizerConfig):
        super().__init__(config)
    
    def save_pretrained(
        self,
        save_directory: Union[str, Path],
        *,
        config: Optional[Union[dict, "DataclassInstance"]] = None,
        repo_id: Optional[str] = None,
        push_to_hub: bool = False,
        **push_to_hub_kwargs,
    ) -> Optional[str]:
        """
        Save weights in local directory.

        Args:
            save_directory (`str` or `Path`):
                Path to directory in which the model weights and configuration will be saved.
            config (`dict` or `DataclassInstance`, *optional*):
                Model configuration specified as a key/value dictionary or a dataclass instance.
            push_to_hub (`bool`, *optional*, defaults to `False`):
                Whether or not to push your model to the Huggingface Hub after saving it.
            repo_id (`str`, *optional*):
                ID of your repository on the Hub. Used only if `push_to_hub=True`. Will default to the folder name if
                not provided.
            kwargs:
                Additional key word arguments passed along to the [`~ModelHubMixin.push_to_hub`] method.
        """
        save_directory = Path(save_directory)
        save_directory.mkdir(parents=True, exist_ok=True)

        # save model weights/files (framework-specific)
        self._save_pretrained(save_directory)

        # push to the Hub if required
        if push_to_hub:
            kwargs = push_to_hub_kwargs.copy()  # soft-copy to avoid mutating input
            if config is not None:  # kwarg for `push_to_hub`
                kwargs["config"] = config
            if repo_id is None:
                repo_id = save_directory.name  # Defaults to `save_directory` name
            return self.push_to_hub(repo_id=repo_id, **kwargs)
        return None

GENRE_TOKEN_LIST = ['Rock', 'Pop', 'Jazz']
GENRE_TOKEN_LIST = ['Genre_Unk'] + ['Genre_'+genre for genre in GENRE_TOKEN_LIST]
GENRE_TOKEN_LIST += ['Genre_'+str(i+1) for i in range(40-len(GENRE_TOKEN_LIST))] #40
BAR2_TOKEN_LIST = ['Bar2_Unk'] + ['Bar2_'+str(i+1) for i in range(127)] # 128

def get_custom_tokenizer():
    TOKENIZER_NAME = CodeplayTokenizer
    config = TokenizerConfig(
        num_velocities=16,
        use_chord=True,
        use_pitch_intervals=True,
        use_programs=True,)
    tokenizer = TOKENIZER_NAME(config)
    
    # MMM tokenizer
    mmm = len(tokenizer)-1
    print(f'MMM Tokenizer bandwith : 0 ~ {mmm}, ({mmm+1} tokens)')
    
    # Add genre token
    for genre_tk in GENRE_TOKEN_LIST:
        tokenizer.add_to_vocab(genre_tk)
    genre = len(tokenizer)-1
    print(f'Genre Tokenizer bandwith : {mmm+1} ~ {genre}, ({genre-mmm} tokens)')
    
    # Add cut(bar4) token
    for cut_tk in BAR2_TOKEN_LIST:
        tokenizer.add_to_vocab(cut_tk)
    # Add cut Unused token
    cut = len(tokenizer)-1
    print(f'Bar2 Cut Tokenizer bandwith : {genre+1} ~ {cut}, ({cut-genre} tokens)')
    
    print(f'Total Tokenizer bandwith : 0 ~ {cut}, ({len(tokenizer)} tokens)')
    return tokenizer

def get_nnn_tokenizer(num_velocities=8):
    NNN = CodeplayTokenizer
    config = TokenizerConfig(
        num_velocities=num_velocities,
        use_programs=True
    )
    tokenizer = NNN(config)
    prev_len = len(tokenizer)
    vocabs = list(tokenizer.vocab.keys())
    
    pitches = [v for v in vocabs if v.startswith('Pitch_') ]
    velocities = [v for v in vocabs if v.startswith('Velocity_') ]
    durations = [v for v in vocabs if v.startswith('Duration_') ]
    
    for p in pitches:
        for v in velocities:
            for d in durations:
                new_tk = f'{p}+{v}+{d}'
                tokenizer.add_to_vocab(new_tk)
    
    print(f'MMM Tokenizer bandwith : 0 ~ {prev_len}, ({prev_len} tokens)')
    print(f'NNN Tokenizer bandwith : {prev_len} ~ {len(tokenizer)}, ({len(tokenizer)-prev_len} tokens)')
    return tokenizer
    
lakh_genres = ['Rock', 'Pop', 'Dance/Electronic', 'Jazz', 'R&B', 'Groove', 'Folk', 'Classical', 'World', 'Metal', "Children"]
lakh_emotions = ['nostalgia', 'excitement', 'love', 'anger', 'happiness', 'sadness','calmness', 'gratitude', 'loneliness', 'anticipation']
lakh_tempos = ['Moderato', 'Allegro', 'Presto', 'Andante']
def get_nnn_meta_tokenizer(num_velocities=4):
    NNN = CodeplayTokenizer
    config = TokenizerConfig(
        num_velocities=num_velocities,
        use_programs=True
    )
    tokenizer = NNN(config)
    mmm_len = len(tokenizer)
    vocabs = list(tokenizer.vocab.keys())
    
    pitches = [v for v in vocabs if v.startswith('Pitch_') ]
    velocities = [v for v in vocabs if v.startswith('Velocity_') ]
    durations = [v for v in vocabs if v.startswith('Duration_') ]
    
    for p in pitches:
        for v in velocities:
            for d in durations:
                new_tk = f'{p}+{v}+{d}'
                tokenizer.add_to_vocab(new_tk)
    nnn_len = len(tokenizer)
    
    # genre tokens
    for genre in lakh_genres:
        tokenizer.add_to_vocab(f'Genre_{genre}')
    genre_len = len(tokenizer)
    
    # emotion tokens
    for emotion in lakh_emotions:
        tokenizer.add_to_vocab(f'Emotion_{emotion}')
    emotion_len = len(tokenizer)
    
    for tempo in lakh_tempos:
        tokenizer.add_to_vocab(f'Tempo_{tempo}')
    tempo_len = len(tokenizer)
    
    print(f'MMM Tokenizer bandwith : 0 ~ {mmm_len}, ({mmm_len} tokens)')
    print(f'NNN Tokenizer bandwith : {mmm_len} ~ {nnn_len}, ({nnn_len-mmm_len} tokens)')
    print(f'Genre Tokenizer bandwith : {nnn_len} ~ {genre_len}, ({genre_len-nnn_len} tokens)')
    print(f'Emotion Tokenizer bandwith : {genre_len} ~ {emotion_len}, ({emotion_len-genre_len} tokens)')
    print(f'Tempo Tokenizer bandwith : {emotion_len} ~ {tempo_len}, ({tempo_len-emotion_len} tokens)')

    return tokenizer