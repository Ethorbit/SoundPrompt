# LICENSE HEADER MANAGED BY add-license-header
#
# Copyright (C) 2025 Ethorbit
#
# This file is part of SoundPrompt.
#
# SoundPrompt is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# SoundPrompt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the
# GNU General Public License along with SoundPrompt.
# If not, see <https://www.gnu.org/licenses/>.
#

import data
from config import load_config
from sentence_transformers import SentenceTransformer

config = load_config()
model_name = config["general"]["model_name"]
model = SentenceTransformer(model_name)

prompt = "rofl"

# user saves
data.update_collection(model=model, library_name="dummy")

# user loads
collection = data.load_collection("dummy")

# user prompts
prompt_embedding = model.encode(prompt)
collection_query = collection.query(
    query_embeddings=[prompt_embedding],
    n_results=10
)

print(collection_query["metadatas"])
