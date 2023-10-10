package it.smartcommunitylabdhub.core.models.builders.entities;

import org.springframework.stereotype.Component;

import it.smartcommunitylabdhub.core.components.fsm.enums.ArtifactState;
import it.smartcommunitylabdhub.core.models.builders.EntityFactory;
import it.smartcommunitylabdhub.core.models.converters.ConversionUtils;
import it.smartcommunitylabdhub.core.models.entities.artifact.Artifact;
import it.smartcommunitylabdhub.core.models.entities.artifact.ArtifactDTO;

@Component
public class ArtifactEntityBuilder {

        /**
         * Build a artifact from a artifactDTO and store extra values as a cbor
         * 
         * @return
         */
        public Artifact build(ArtifactDTO artifactDTO) {
                return EntityFactory.combine(
                                ConversionUtils.convert(artifactDTO, "artifact"), artifactDTO,
                                builder -> builder
                                                .with(p -> p.setMetadata(
                                                                ConversionUtils.convert(artifactDTO
                                                                                .getMetadata(),
                                                                                "metadata")))
                                                .with(a -> a.setExtra(
                                                                ConversionUtils.convert(artifactDTO
                                                                                .getExtra(),

                                                                                "cbor")))
                                                .with(a -> a.setSpec(
                                                                ConversionUtils.convert(artifactDTO
                                                                                .getSpec(),

                                                                                "cbor"))));

        }

        /**
         * Update a artifact if element is not passed it override causing empty field
         * 
         * @param artifact
         * @return
         */
        public Artifact update(Artifact artifact, ArtifactDTO artifactDTO) {
                return EntityFactory.combine(
                                artifact, artifactDTO, builder -> builder
                                                .with(a -> a.setKind(artifactDTO.getKind()))
                                                .with(a -> a.setProject(artifactDTO.getProject()))
                                                .with(a -> a.setState(artifactDTO.getState() == null
                                                                ? ArtifactState.CREATED
                                                                : ArtifactState.valueOf(
                                                                                artifactDTO.getState())))
                                                .with(a -> a.setMetadata(
                                                                ConversionUtils.convert(artifactDTO
                                                                                .getMetadata(),

                                                                                "metadata")))
                                                .with(a -> a.setExtra(
                                                                ConversionUtils.convert(artifactDTO
                                                                                .getExtra(),

                                                                                "cbor")))
                                                .with(a -> a.setSpec(
                                                                ConversionUtils.convert(artifactDTO
                                                                                .getSpec(),

                                                                                "cbor")))
                                                .with(a -> a.setEmbedded(
                                                                artifactDTO.getEmbedded())));
        }
}
