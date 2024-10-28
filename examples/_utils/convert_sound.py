__all__ = ("convert_sound", )


def convert_sound(source: bytes, *, in_format="wav", out_format="wav", out_codec="pcm_s16le") -> bytes:
    '''
    Converts an audio source to another format using ffmpeg.
    '''
    import subprocess

    ffmpeg_cmd = (
        "ffmpeg",
        "-f", in_format,
        "-i", "pipe:0",  # stdin
        "-f", out_format,
        "-codec:a", out_codec,
        "pipe:1",  # stdout
    )
    p = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
    return p.communicate(source)[0]
